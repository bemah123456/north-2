# Builds a small synthetic 4AT answer set with Windows' built-in voices, for checking how often
# speech-recognition mistakes would flip a correct answer to "wrong" (false positive) or a
# wrong answer to "right" (missed impairment). Synthetic voices are NOT older speakers;
# this is a pipeline check, not clinical validation.
# Usage: powershell -File make_probes.ps1   -> training\probes\*.wav + probes.json

$ErrorActionPreference = 'Stop'
$out = Join-Path $PSScriptRoot 'probes'
New-Item -ItemType Directory -Force $out | Out-Null
Add-Type -AssemblyName System.Speech

# kind: months | age | birth | place | year ; healthy = correct answer for the test person
# (age 84, born 4 May 1942, at home, year 2026)
$items = @(
  @{ id='m_full';     kind='months'; healthy=$true;  text='December, November, October, September, August, July, June, May, April, March, February, January' },
  @{ id='m_slow';     kind='months'; healthy=$true;  text='December... November... um... October... September... August... uh... July... June' },
  @{ id='m_repeat';   kind='months'; healthy=$true;  text='December, November, November, October, September, August, July, June, May' },
  @{ id='m_stop4';    kind='months'; healthy=$false; text='December, November, October, September... I am not sure' },
  @{ id='m_skip';     kind='months'; healthy=$false; text='December, November, September, August, June, May, April' },
  @{ id='m_forward';  kind='months'; healthy=$false; text='January, February, March, April, May, June, July' },
  @{ id='m_drift';    kind='months'; healthy=$false; text='December, November, October, November, December, January' },
  @{ id='a_ok';       kind='age';    healthy=$true;  text="I'm eighty four" },
  @{ id='a_wrong';    kind='age';    healthy=$false; text="I'm sixty two" },
  @{ id='b_ok';       kind='birth';  healthy=$true;  text='The fourth of May, nineteen forty two' },
  @{ id='b_wrong';    kind='birth';  healthy=$false; text='The ninth of March, nineteen fifty' },
  @{ id='p_ok';       kind='place';  healthy=$true;  text="We're at home, in my house" },
  @{ id='p_wrong';    kind='place';  healthy=$false; text="We're at the train station" },
  @{ id='y_ok';       kind='year';   healthy=$true;  text='It is twenty twenty six' },
  @{ id='y_wrong';    kind='year';   healthy=$false; text='Nineteen ninety, I think' }
)

$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = $s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }
$rows = @()
foreach ($v in $voices) {
  foreach ($rate in -4, -1, 2) {
    $s.SelectVoice($v); $s.Rate = $rate
    foreach ($it in $items) {
      $name = "{0}_{1}_r{2}.wav" -f $it.id, ($v -split ' ')[1], $rate
      $path = Join-Path $out $name
      $s.SetOutputToWaveFile($path)
      $s.Speak($it.text)
      $s.SetOutputToNull()
      $rows += [ordered]@{ path=$path; id=$it.id; kind=$it.kind; healthy=$it.healthy; text=$it.text; voice=$v; rate=$rate }
    }
  }
}
$s.Dispose()
$rows | ConvertTo-Json -Depth 3 | Out-File -Encoding utf8 (Join-Path $out 'probes.json')
"{0} probe clips written to {1}" -f $rows.Count, $out
