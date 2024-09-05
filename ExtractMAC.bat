@echo off
set output_file=MACAddresses.txt

rem Clear the output file if it exists
if exist "%output_file%" del "%output_file%"

rem Run ipconfig /all, filter for physical addresses, and extract only the MAC addresses
for /F "tokens=2 delims=:" %%A in ('ipconfig /all ^| findstr /R "Physical"') do (
    for /F "tokens=* delims= " %%B in ("%%A") do (
        echo %%B>>"%output_file%"
    )
)

rem Notify the user
echo MAC addresses have been saved to %output_file%.

pause