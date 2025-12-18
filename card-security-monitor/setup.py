from setuptools import setup, find_packages

setup(
    name="card-security-monitor",
    version="1.0.0",
    description="Monitor de segurança para detecção de dados de cartão de crédito em páginas de pagamento",
    author="Security Team",
    python_requires=">=3.8",
    py_modules=["monitor", "alert", "main"],
    install_requires=[
        "pynput==1.7.6",
        "Pillow==10.1.0",
        "pywin32==306",
        "psutil==5.9.6",
        "uiautomation==2.0.37",
    ],
    entry_points={
        "console_scripts": [
            "card-security-monitor=main:main",
        ],
    },
)
