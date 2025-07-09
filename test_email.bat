@echo off
echo 📧 Email Testing Tool
echo ====================

if "%1"=="" (
    echo.
    echo Usage: test_email.bat [command]
    echo.
    echo Commands:
    echo   config  - Test email configuration
    echo   test    - Send a test email
    echo   sample  - Send a sample trade email
    echo   stats   - Show email statistics
    echo   debug   - Show comprehensive debug info
    echo   all     - Run all tests
    echo.
    echo Examples:
    echo   test_email.bat config
    echo   test_email.bat test
    echo   test_email.bat all
    goto :end
)

python test_email.py %1

:end
pause
