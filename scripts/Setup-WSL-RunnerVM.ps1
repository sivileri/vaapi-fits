$spaceRequired = 15.0
$destination="invalid"

if ((Test-Path D:\) -and ([math]::round((Get-Volume -DriveLetter D | Select-Object SizeRemaining).SizeRemaining /1Gb, 3) -gt $spaceRequired)) {
    $destination="D:\"
} else {
    if ((Test-Path E:\) -and ([math]::round((Get-Volume -DriveLetter E | Select-Object SizeRemaining).SizeRemaining /1Gb, 3) -gt $spaceRequired)) {
        $destination="E:\"
    } else {
        if ((Test-Path F:\) -and ([math]::round((Get-Volume -DriveLetter F | Select-Object SizeRemaining).SizeRemaining /1Gb, 3) -gt $spaceRequired)) {
            $destination="F:\"
        } else {
            if ((Test-Path C:\) -and ([math]::round((Get-Volume -DriveLetter C | Select-Object SizeRemaining).SizeRemaining /1Gb, 3) -gt $spaceRequired)) {
                $destination="C:\UbuntuRunnerFiles"
            }
        }
    }
}

if ($destination -eq "invalid"){
    "Could not find a disk drive with at least $spaceRequired GB free"
    Exit
}

"Choosing destination: $destination with at least $spaceRequired GB of free space."

"List of installed WSL distros:"
wsl --list
if (-not((wsl --list) -replace "`0" | Select-String -Pattern Ubuntu -Quiet)) {

    "Ubuntu not detected in wsl --list, installing..."

    if (-not(Test-Path $destination\ubuntu.zip)) {
        # Hide the progress bar to avoid download slowdown
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri https://aka.ms/wslubuntu2204 -OutFile $destination\ubuntu.zip -UseBasicParsing
        $ProgressPreference = "Continue"
    }
    
    if (-not(Test-Path $destination\UbuntuInstall)) {
        Expand-Archive $destination\ubuntu.zip -DestinationPath $destination\UbuntuInstall
        mv $destination\UbuntuInstall\Ubuntu_2204.1.7.0_x64.appx $destination\UbuntuInstall\Ubuntu_2204.1.7.0_x64.zip
    }
    
    if (-not(Test-Path $destination\UbuntuInstall\x64)) {
        Expand-Archive $destination\UbuntuInstall\Ubuntu_2204.1.7.0_x64.zip -DestinationPath $destination\UbuntuInstall\x64
    }
    
    cd $destination\UbuntuInstall\x64
    .\ubuntu.exe install --root
}

if (-not(Test-Path \\wsl.localhost\Ubuntu\home\wslrunner)) {
    pushd $destination\UbuntuInstall\x64
    "Creating wslrunner user in Ubuntu distro image..."
    .\ubuntu.exe run -u root useradd -m wslrunner
    .\ubuntu.exe run -u root 'echo wslrunner:wslrunner | chpasswd'
    .\ubuntu.exe run -u root 'chsh -s /bin/bash wslrunner'
    .\ubuntu.exe run -u root 'usermod -aG sudo wslrunner'
    .\ubuntu.exe run -u root "echo 'wslrunner ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers"
    popd # $destination\UbuntuInstall\x64
}

"Ubuntu detected in wsl --list, using existing Ubuntu version:"
wsl -d Ubuntu -u wslrunner --cd ~ lsb_release -r
if (-not(wsl -d Ubuntu -u wslrunner --cd ~ lsb_release -r | Select-String "22.10" -Quiet)) {
    if (-not(wsl -d Ubuntu -u wslrunner --cd ~ lsb_release -r | Select-String "22.04" -Quiet)) {
        Write-Error "When using the pre-existing Ubuntu distro, the version must be 22.04 or 22.10"
    }
}

if (-not(Test-Path \\wsl.localhost\Ubuntu\home\wslrunner\d3d12libs)) {
    "Provisioning d3d12 libs into /home/wslrunner/d3d12libs/"
    mkdir -p \\wsl.localhost\Ubuntu\home\wslrunner\d3d12libs\
    cp $destination\d3d12libs\*.so \\wsl.localhost\Ubuntu\home\wslrunner\d3d12libs\
}

"Provisioning latest run-tests.sh into /home/wslrunner/d3d12libs/"
Invoke-WebRequest -Uri https://raw.githubusercontent.com/sivileri/vaapi-fits/devel_mesad3d12/scripts/run-tests.sh -OutFile \\wsl.localhost\Ubuntu\home\wslrunner\run-tests.sh -UseBasicParsing

wsl -d Ubuntu --cd ~ chmod +x /home/wslrunner/run-tests.sh
wsl -d Ubuntu -u wslrunner --cd ~ /home/wslrunner/run-tests.sh
