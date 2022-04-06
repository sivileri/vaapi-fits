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
if (-not((wsl --list) -replace "`0" | Select-String -Pattern Ubuntu-22.04 -Quiet)) {

    "wslrunner Ubuntu-22.04 not detected in wsl --list, installing..."

    if (-not(Test-Path $destination\ubuntu.zip)) {
        Invoke-WebRequest -Uri https://aka.ms/wslubuntu2204 -OutFile $destination\ubuntu.zip -UseBasicParsing
    }
    
    if (-not(Test-Path $destination\UbuntuInstall)) {
        Expand-Archive $destination\ubuntu.zip -DestinationPath $destination\UbuntuInstall
        mv $destination\UbuntuInstall\Ubuntu_2204.0.10.0_x64.appx $destination\UbuntuInstall\Ubuntu_2204.0.10.0_x64.zip
    }
    
    if (-not(Test-Path $destination\UbuntuInstall\x64)) {
        Expand-Archive $destination\UbuntuInstall\Ubuntu_2204.0.10.0_x64.zip -DestinationPath $destination\UbuntuInstall\x64
    }
    
    cd $destination\UbuntuInstall\x64
    
    .\ubuntu2204.exe install --root
    .\ubuntu2204.exe run useradd -m wslrunner
    .\ubuntu2204.exe run 'echo wslrunner:wslrunner | chpasswd'
    .\ubuntu2204.exe run 'chsh -s /bin/bash wslrunner'
    .\ubuntu2204.exe run 'usermod -aG sudo wslrunner'
    .\ubuntu2204.exe run "echo 'wslrunner ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers"
} else {
    "wslrunner Ubuntu-22.04 detected in wsl --list, using that distro..."
}

# Copy test assets into Ubuntu-22.04 wslrunner home dir
if (-not(Test-Path \\wsl.localhost\Ubuntu-22.04\home\wslrunner\assets.tar.gz)) {
    "Provisioning test assets into /home/wslrunner/assets.tar.gz"
    cp $destination\assets.tar.gz \\wsl.localhost\Ubuntu-22.04\home\wslrunner\assets.tar.gz
}
if (-not(Test-Path \\wsl.localhost\Ubuntu-22.04\home\wslrunner\d3d12libs)) {
    "Provisioning d3d12 libs into /home/wslrunner/d3d12libs/"
    mkdir -p \\wsl.localhost\Ubuntu-22.04\home\wslrunner\d3d12libs\
    cp $destination\d3d12libs\*.so \\wsl.localhost\Ubuntu-22.04\home\wslrunner\d3d12libs\
}

"Provisioning latest run-tests.sh into /home/wslrunner/d3d12libs/"
Invoke-WebRequest -Uri https://raw.githubusercontent.com/sivileri/vaapi-fits/user/sivileri/vaapifits_mesad3d12/scripts/run-tests.sh -OutFile \\wsl.localhost\Ubuntu-22.04\home\wslrunner\run-tests.sh -UseBasicParsing

wsl -d Ubuntu-22.04 --cd ~ chmod +x /home/wslrunner/run-tests.sh
wsl -d Ubuntu-22.04 -u wslrunner --cd ~ /home/wslrunner/run-tests.sh
