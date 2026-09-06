[CmdletBinding()]
param(
    [string]$SourceRoot = 'C:\qpathformer_enterprise_v2',
    [string]$CandidateRoot = 'C:\qpathformer_enterprise_v2_release',
    [string]$RecordsRoot = 'C:\qpathformer_enterprise_v2_release_records',
    [string]$PaperRoot = 'C:\qpathformer_tr010',
    [string]$DownloadsRoot = (Join-Path $HOME 'Downloads'),
    [string]$TargetRoot = 'C:\qpathformer_enterprise_v2_private',
    [Parameter(Mandatory)][string]$OverlayRoot,
    [Parameter(Mandatory)][string]$AuditRoot,
    [switch]$PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$TargetRoot = [IO.Path]::GetFullPath($TargetRoot).TrimEnd('\')
if ($TargetRoot -ine 'C:\qpathformer_enterprise_v2_private') {
    throw 'This preparation is authorized only for the named private workspace.'
}
if (Test-Path -LiteralPath $TargetRoot) { throw 'Target already exists; nothing will be overwritten.' }

function Assert-PlainPath([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse path rejected: $current"
            }
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }
}

function Get-Inventory([string]$Root) {
    Assert-PlainPath $Root
    $rootPath = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
    $found = [Collections.Generic.List[object]]::new()
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($rootPath)
    while ($pending.Count) {
        foreach ($item in Get-ChildItem -LiteralPath $pending.Pop() -Force) {
            if ($item.Name -eq '.git') { continue }
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Reparse item rejected: $($item.FullName)"
            }
            if ($item.PSIsContainer) { $pending.Push($item.FullName); continue }
            $relative = [IO.Path]::GetRelativePath($rootPath, $item.FullName).Replace('\','/')
            $found.Add([ordered]@{
                path = $relative
                bytes = $item.Length
                sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            })
        }
    }
    return @($found | Sort-Object { $_.path })
}

function Write-Json([string]$Path, $Value) {
    $parent = Split-Path -Parent $Path
    [IO.Directory]::CreateDirectory($parent) | Out-Null
    $json = ($Value | ConvertTo-Json -Depth 40).Replace("`r`n", "`n") + "`n"
    [IO.File]::WriteAllText($Path, $json, [Text.UTF8Encoding]::new($false))
}

function Target-Path([string]$Relative) {
    if ($Relative -match '(^/|\\|:|(^|/)\.\.(/|$))') { throw "Unsafe destination: $Relative" }
    $path = [IO.Path]::GetFullPath((Join-Path $TargetRoot $Relative))
    if (-not $path.StartsWith($TargetRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw "Destination escapes target: $Relative"
    }
    Assert-PlainPath $path
    return $path
}

$roots = [ordered]@{
    source_baseline = (Resolve-Path -LiteralPath $SourceRoot).Path
    corrected_candidate = (Resolve-Path -LiteralPath $CandidateRoot).Path
    release_records = (Resolve-Path -LiteralPath $RecordsRoot).Path
    earlier_tr010 = (Resolve-Path -LiteralPath $PaperRoot).Path
}
$OverlayRoot = (Resolve-Path -LiteralPath $OverlayRoot).Path
$AuditRoot = [IO.Path]::GetFullPath($AuditRoot)
Assert-PlainPath $TargetRoot
Assert-PlainPath $OverlayRoot
Assert-PlainPath $AuditRoot
foreach ($root in @($roots.Values) + @($OverlayRoot)) {
    if ($AuditRoot.StartsWith($root.TrimEnd('\') + '\', [StringComparison]::OrdinalIgnoreCase) -or $AuditRoot -ieq $root) {
        throw 'Audit outputs must be outside all inspected roots and the overlay.'
    }
}
$before = [ordered]@{}
foreach ($id in $roots.Keys) { $before[$id] = @(Get-Inventory $roots[$id]) }
Write-Json (Join-Path $AuditRoot 'source_inventory_before.json') $before
$head = (& git --no-optional-locks -C $SourceRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -ne 'cf9721afb81273d82667dd7b33ee5e5f3ad806d9') {
    throw 'Unexpected source Git anchor; review before preparation.'
}
$inventoryHash = (Get-FileHash -LiteralPath (Join-Path $CandidateRoot 'release/PUBLICATION_INVENTORY.json')).Hash.ToLowerInvariant()
$checksumsHash = (Get-FileHash -LiteralPath (Join-Path $CandidateRoot 'release/SHA256SUMS.txt')).Hash.ToLowerInvariant()
if ($inventoryHash -ne 'bed0957ddb1de0b3ed1b76c295f7febc12f7ca53880d7c1fd408996c2bcc07e6' -or
    $checksumsHash -ne '47a04a06dcc3595402c95f8028c0cf222ccc09351040b9a3fb76f399e87dbf75') {
    throw 'Corrected candidate manifest identity changed.'
}
$candidateMap = @{}
foreach ($item in $before.corrected_candidate) { $candidateMap[$item.path] = $item }
$listed = @{}
foreach ($line in Get-Content -LiteralPath (Join-Path $CandidateRoot 'release/SHA256SUMS.txt')) {
    if ($line -notmatch '^([a-fA-F0-9]{64})\s+\*?(.+)$') { throw 'Invalid historical checksum entry.' }
    $digest = $Matches[1].ToLowerInvariant()
    $relative = $Matches[2].Replace('\','/')
    if (-not $candidateMap.ContainsKey($relative) -or $candidateMap[$relative].sha256 -ne $digest) {
        throw "Historical checksum mismatch: $relative"
    }
    $listed[$relative] = $true
}
if ($candidateMap.Count -ne $listed.Count + 1) { throw 'Unexpected historical candidate files.' }

$selection = [Collections.Generic.List[object]]::new()
$exclusions = [Collections.Generic.List[object]]::new()
$catalogue = [Collections.Generic.List[object]]::new()
$destinations = @{}
foreach ($id in $roots.Keys) {
    foreach ($file in $before[$id]) {
        $rel = $file.path
        $destination = $null
        $role = 'reference_only'
        $reason = 'Historical source reference retained externally; candidate is the chosen copy source.'
        if ($id -eq 'corrected_candidate') {
            $reason = 'Not required for local code preparation; retained in original candidate with this hash.'
            if ($rel -in @('LICENSE','QPATHFORMER-PLATFORM-1.0.txt','CONTRIBUTORS.md','requirements-crypto.txt','requirements-release.txt')) {
                $destination = $rel; $role = 'retained_notice_or_dependency_pin'
            } elseif ($rel -eq 'scripts/validate_v2_release.py') {
                $destination = 'docs/history/tooling/validate_v2_release.py'; $role = 'historical_tooling'
            } elseif ($rel -like 'scripts/*.py') {
                $destination = $rel; $role = 'inherited_implementation'
            } elseif ($rel -like 'scripts/*.ps1' -or $rel -like 'scripts/*.md') {
                $destination = 'docs/history/tooling/' + $rel; $role = 'historical_tooling'
            } elseif ($rel -like 'tests/unit/*.py' -or $rel -like 'shared/models/qpathformer/*.py') {
                $destination = $rel; $role = 'inherited_code_or_synthetic_unit_test'
            } elseif ($rel -like 'shared/configs/*' -or $rel -like 'shared/schemas/*.schema.json' -or
                $rel -eq 'shared/registry/run_registry.schema.json' -or $rel -like 'shared/registry/examples/*') {
                $destination = $rel; $role = 'configuration_schema_or_empty_template'
            } elseif ($rel -like 'shared/standards/access_pod/vendor/*' -and [IO.Path]::GetExtension($rel) -ne '.pdf') {
                $destination = $rel; $role = 'vendored_mit_text_subset'
            } elseif ($rel -like 'shared/standards/access_pod/mappers/*' -or
                $rel -like 'shared/standards/access_pod/profiles/*' -or $rel -like 'shared/standards/access_pod/schemas/*') {
                $destination = $rel; $role = 'enterprise_standards_bridge_definition'
            } elseif ($rel -like 'docs/execution/*.md') {
                $destination = 'docs/history/execution/' + $rel.Substring('docs/execution/'.Length); $role = 'historical_runbook'
            } elseif ($rel -like 'docs/release/*.md') {
                $destination = 'docs/history/public_release_docs/' + $rel.Substring('docs/release/'.Length); $role = 'historical_release_document'
            } elseif ($rel -like 'release/*' -or $rel -in @('SOURCE_PROVENANCE.json','REPOSITORY_MANIFEST.json','dev_assist.md')) {
                $destination = 'release/provenance/historical_candidate/' + $rel; $role = 'historical_candidate_record'
            }
            if ($rel -match '\.(pdf|docx|zip|jsonl|safetensors|bin|pt|pth|pem|key)$' -or $rel -like 'path_*' -or
                $rel -like 'shared/standards/access_pod/generated/*' -or $rel -like 'shared/models/evaluation/*') {
                $destination = $null
                $reason = 'Paper, derived data, bulk historical output, archive or model asset excluded from private preparation.'
            }
        } elseif ($id -eq 'release_records') {
            if ($rel -notlike 'LICENCE_REVIEW/*' -and [IO.Path]::GetExtension($rel) -in @('.md','.json')) {
                $destination = 'release/provenance/historical_records/' + $rel; $role = 'historical_gate_or_drafting_record'
            } else { $reason = 'Superseded legal-review draft or historical archive retained externally, not adopted or imported.' }
        } elseif ($id -eq 'earlier_tr010') { $reason = 'Earlier manuscript/review retained externally; not the current paper.' }

        $catalogue.Add([ordered]@{ source_id=$id; source_relative_path=$rel; bytes=$file.bytes; sha256=$file.sha256; selected=($null -ne $destination) })
        if ($null -ne $destination) {
            if ($destinations.ContainsKey($destination.ToLowerInvariant())) { throw "Destination collision: $destination" }
            $destinations[$destination.ToLowerInvariant()] = $true
            $immutable = $role.StartsWith('historical_') -or $role -eq 'vendored_mit_text_subset'
            $selection.Add([ordered]@{
                source_id=$id; source_relative_path=$rel; source_bytes=$file.bytes; source_sha256=$file.sha256
                destination_path=$destination; destination_sha256=$file.sha256; transformation='none_preserve_bytes'
                role=$role; immutable_copy=$immutable
                rights_treatment=$(if ($role -eq 'vendored_mit_text_subset') { 'Retain nested MIT notice; selected subset only.' } else { 'Retain source notices; local preparation is not distribution clearance.' })
            })
        } else {
            $exclusions.Add([ordered]@{ source_id=$id; source_relative_path=$rel; bytes=$file.bytes; sha256=$file.sha256; reason=$reason })
        }
    }
}
$overlay = @(Get-Inventory $OverlayRoot)
foreach ($file in $overlay) {
    if ($destinations.ContainsKey($file.path.ToLowerInvariant())) { throw "Overlay would overwrite imported file: $($file.path)" }
}
$plan = [ordered]@{ target=$TargetRoot; selected_files=$selection.Count; overlay_files=$overlay.Count; excluded_files=$exclusions.Count; source_files=$catalogue.Count; source_head=$head; git_or_network_actions=$false }
Write-Json (Join-Path $AuditRoot 'preparation_plan.json') $plan
Write-Json (Join-Path $AuditRoot 'planned_selection.json') $selection.ToArray()
if ($PlanOnly) { $plan | ConvertTo-Json; return }

[IO.Directory]::CreateDirectory($TargetRoot) | Out-Null
foreach ($entry in $selection) {
    $from = Join-Path $roots[$entry.source_id] $entry.source_relative_path
    $to = Target-Path $entry.destination_path
    Assert-PlainPath $from
    if ((Get-FileHash -LiteralPath $from).Hash.ToLowerInvariant() -ne $entry.source_sha256) { throw 'Source changed during selection.' }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $to)) | Out-Null
    Copy-Item -LiteralPath $from -Destination $to -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $to).Hash.ToLowerInvariant() -ne $entry.destination_sha256) { throw 'Copy verification failed.' }
}
foreach ($file in $overlay) {
    $to = Target-Path $file.path
    [IO.Directory]::CreateDirectory((Split-Path -Parent $to)) | Out-Null
    Copy-Item -LiteralPath (Join-Path $OverlayRoot $file.path) -Destination $to -ErrorAction Stop
    if ((Get-FileHash -LiteralPath $to).Hash.ToLowerInvariant() -ne $file.sha256) { throw 'Overlay changed during copy.' }
}

$stages = @('01_source','02_signals','03_dataset','04_state1_package','05_runs','06_review','07_logs')
$paths = @('path_1_tr_corpus_reference','path_2_access_mode_canonical','path_3_external_custom_adapter')
$emptyFolders = [Collections.Generic.List[string]]::new()
foreach ($path in $paths) { $emptyFolders.Add($path); foreach ($stage in $stages) { $emptyFolders.Add("$path/$stage") } }
foreach ($path in @('path_1_tr_corpus_reference/01_source/tr_docs','path_1_tr_corpus_reference/01_source/readme_refs',
    'path_1_tr_corpus_reference/01_source/corpus_snapshot','path_3_external_custom_adapter/01_source/inbound',
    'shared/runtime','shared/models/evaluation','evidence/historical_v1','evidence/v2_validation','release/private_baseline','docs/architecture')) {
    $emptyFolders.Add($path)
}
foreach ($folder in $emptyFolders) {
    $to = Target-Path ($folder + '/README.md')
    if (Test-Path -LiteralPath $to) { throw 'Unexpected scaffold collision.' }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $to)) | Out-Null
    $body = "# Reserved: $folder`n`nThis stage is intentionally not populated with historical data or outputs.`nUse the root README, local-check guide and release/provenance index.`nFuture runs need isolated inputs, registry and output paths with explicit scope.`nThis placeholder does not grant training, scoring, sharing or publication authority.`n"
    [IO.File]::WriteAllText($to, $body, [Text.UTF8Encoding]::new($false))
}

$now = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$base = 'release/provenance/'
Write-Json (Target-Path ($base+'SOURCE_SELECTION.json')) ([ordered]@{ schema_version='private_selection_v1'; created_at_utc=$now; status='LOCAL_PREPARATION_NOT_UPLOAD_CLEARANCE'; files=$selection.ToArray() })
Write-Json (Target-Path ($base+'SOURCE_CATALOGUE.json')) ([ordered]@{ scope='Non-Git regular files in four original roots; no contents imported by this catalogue.'; files=$catalogue.ToArray() })
Write-Json (Target-Path ($base+'EXCLUSIONS.json')) ([ordered]@{ scope='Selection exclusions, not deletions or legal conclusions.'; files=$exclusions.ToArray() })
Write-Json (Target-Path ($base+'SOURCE_ANCHORS.json')) ([ordered]@{
    created_at_utc=$now; current_status='LOCAL_PRIVATE_DEVELOPMENT_PREPARATION'
    source_repository=[ordered]@{ url='https://github.com/qpathformer/qpathformer-enterprise-v1.0-release.git'; commit=$head;
        tree=((& git --no-optional-locks -C $SourceRoot rev-parse 'HEAD^{tree}').Trim()); tag='v2.0-qpathformer-enterprise-source-baseline';
        tag_object=((& git --no-optional-locks -C $SourceRoot rev-parse 'refs/tags/v2.0-qpathformer-enterprise-source-baseline').Trim()) }
    candidate=[ordered]@{ source_id='corrected_candidate'; file_count=$before.corrected_candidate.Count; publication_inventory_sha256=$inventoryHash;
        checksum_file_sha256=$checksumsHash; checksum_entries_verified=$listed.Count; status='HISTORICAL_READY_FOR_M12_RECONSIDERATION_NOT_CURRENT_APPROVAL' }
    intended_remote=[ordered]@{ owner='qpathformer'; repository_name=$null; visibility_intent='private'; configured=$false; creation_authorized=$false; push_authorized=$false }
    decision_boundaries=@('No M00 restart','No licence adoption','No source implementation changes','No commit/tag/remote/push','Historical gate records do not approve this workspace')
})

$externalPaths = [ordered]@{
    current_tr010 = (Join-Path $SourceRoot 'tr10 - Fail-Closed Governed Dataset Lifecycles (23) - Rights and Provenance Integrated 20260721.docx')
    research_licence_review = (Join-Path $DownloadsRoot 'QPATHFORMER-RESEARCH-STANDARDS-EXPLORATION-LICENCE-1.1-THIRD-PASS-RECONCILED-LEGAL-REVIEW-CANDIDATE-20260719.md')
    historical_rights_notice = (Join-Path $DownloadsRoot 'qpathformer-v2-tr-pre-rebuild-review/ACCESS-POD-HISTORICAL-MATERIALS-RIGHTS-CONFIRMATION-AND-DISTRIBUTION-NOTICE-PRE-REBUILD-DECISION-REVIEW-DRAFT-20260721.md')
    licence_history = (Join-Path $DownloadsRoot 'LICENSE_HISTORY.md')
    latest_review = (Join-Path $DownloadsRoot 'APOD-TR-010_READ_ONLY_REVIEW_AND_PRIVATE_DEVELOPMENT_PLAN_20260905.md')
}
$external = @()
foreach ($id in $externalPaths.Keys) {
    Assert-PlainPath $externalPaths[$id]
    $f = Get-Item -LiteralPath $externalPaths[$id]
    $external += [ordered]@{ reference_id=$id; name=$f.Name; bytes=$f.Length; sha256=(Get-FileHash -LiteralPath $f.FullName).Hash.ToLowerInvariant(); imported=$false; status='EXTERNAL_REFERENCE_NOT_ADOPTED' }
}
Write-Json (Target-Path ($base+'EXTERNAL_REFERENCES.json')) ([ordered]@{ references=$external; claims='Hashes identify referenced documents; they do not grant permissions.' })
Write-Json (Target-Path '.local/provenance/LOCAL_SOURCE_PATHS.json') ([ordered]@{ roots=$roots; external_paths=$externalPaths; purpose='Ignored local locators; portable IDs and hashes are tracked separately.' })

$vendor = 'shared/standards/access_pod/vendor/access-pod-artifacts-core/v1a/'
$manifest = Get-Content -LiteralPath (Target-Path ($vendor+'manifest_v1a_pack.json')) -Raw | ConvertFrom-Json
$retained = @()
$omitted = @()
foreach ($entry in $selection | Where-Object { $_.role -eq 'vendored_mit_text_subset' }) {
    $relative = $entry.destination_path.Substring($vendor.Length)
    $original = @($manifest.files | Where-Object { $_.relative_path -eq $relative })
    $record = [ordered]@{ destination_path=$entry.destination_path; physical_sha256=$entry.destination_sha256; physical_bytes=$entry.source_bytes; comparison='PROVENANCE_METADATA_NOT_MANIFEST_ENTRY' }
    if ($original.Count -eq 1) {
        $record.manifest_sha256 = $original[0].sha256
        $record.manifest_bytes = $original[0].bytes
        $bytes = [IO.File]::ReadAllBytes((Target-Path $entry.destination_path))
        if ($entry.destination_sha256 -eq $record.manifest_sha256 -and $bytes.Length -eq $record.manifest_bytes) {
            $record.comparison = 'BYTE_MATCH'
        } else {
            # Decode and encode as Latin-1 to change only exact CRLF byte pairs.
            $canonical = [Text.Encoding]::Latin1.GetBytes([Text.Encoding]::Latin1.GetString($bytes).Replace("`r`n","`n"))
            $sha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($canonical)).ToLowerInvariant()
            if ($sha -ne $record.manifest_sha256 -or $canonical.Length -ne $record.manifest_bytes) { throw 'Unexpected vendor canonical mismatch.' }
            $record.comparison = 'CANONICAL_LF_MATCH'
            $record.canonical_sha256 = $sha
        }
    }
    $retained += $record
}
foreach ($entry in $manifest.files) {
    if (-not (Test-Path -LiteralPath (Target-Path ($vendor+$entry.relative_path)))) {
        $omitted += [ordered]@{ path=$entry.relative_path; manifest_sha256=$entry.sha256; reason='PDF intentionally not imported; original retained externally.' }
    }
}
Write-Json (Target-Path ($base+'STANDARDS_SUBSET.json')) ([ordered]@{ status='SELECTED_SUBSET_NOT_FULL_PACK'; physical_bytes_modified=$false; retained_files=$retained; omitted_manifest_entries=$omitted })

$allNow = @(Get-Inventory $TargetRoot)
$generated = @($allNow | Where-Object { -not $destinations.ContainsKey($_.path.ToLowerInvariant()) -and $_.path -notlike '.local/*' })
Write-Json (Target-Path ($base+'GENERATED_FILES.json')) ([ordered]@{ status='PREPARATION_IDENTITIES_NOT_RELEASE_SEAL'; excludes=@('this self-referencing file','later validation records','Git metadata','ignored local locators'); files=$generated })
$after = [ordered]@{}
$sourceChanges = @()
foreach ($id in $roots.Keys) {
    $after[$id] = @(Get-Inventory $roots[$id])
    $old = $before[$id] | ConvertTo-Json -Depth 5 -Compress
    $new = $after[$id] | ConvertTo-Json -Depth 5 -Compress
    if ($old -cne $new) { $sourceChanges += $id }
}
Write-Json (Join-Path $AuditRoot 'source_inventory_after.json') $after
Write-Json (Target-Path 'release/private_baseline/SOURCE_PRESERVATION_CHECK.json') ([ordered]@{
    status=$(if ($sourceChanges.Count) {'FAIL'} else {'PASS'}); changed_source_roots=$sourceChanges;
    roots_verified=@($roots.Keys); total_regular_files=$catalogue.Count; method='Before/after path, size and SHA-256 comparison; Git internals excluded.'
})
if ($sourceChanges.Count) { throw 'Original files changed during preparation; stop for review.' }
$plan | ConvertTo-Json
