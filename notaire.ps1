<#
.SYNOPSIS
    NotaireAI - Script PowerShell pour Windows

.DESCRIPTION
    Raccourci pour executer generer_acte.py depuis n'importe quel dossier.

.EXAMPLE
    .\notaire.ps1
    .\notaire.ps1 --quick
    .\notaire.ps1 --type vente -d donnees.json

.NOTES
    Version: 1.3.0
#>

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "python"

# Executer le script principal
& $Python "$ScriptDir\generer_acte.py" @Args
