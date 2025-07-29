#!/bin/bash

# Set package name and version
PACKAGE_NAME="deepseek-desktop-py"
VERSION="1.0"

# Create directory structure
mkdir -p ${PACKAGE_NAME}/DEBIAN \
         ${PACKAGE_NAME}/usr/share/applications \
         ${PACKAGE_NAME}/usr/share/icons/hicolor/256x256/apps \
         ${PACKAGE_NAME}/usr/local/bin \
         ${PACKAGE_NAME}/opt/${PACKAGE_NAME}

# Copy application files
cp main.py ${PACKAGE_NAME}/opt/${PACKAGE_NAME}/
cp icon.png ${PACKAGE_NAME}/opt/${PACKAGE_NAME}/
cp icon.png ${PACKAGE_NAME}/usr/share/icons/hicolor/256x256/apps/${PACKAGE_NAME}.png

# Create desktop entry
cat > ${PACKAGE_NAME}/usr/share/applications/${PACKAGE_NAME}.desktop <<EOL
[Desktop Entry]
Name=DeepSeek Desktop
Comment=DeepSeek Desktop Client
Exec=/usr/local/bin/${PACKAGE_NAME}
Icon=${PACKAGE_NAME}
Terminal=false
Type=Application
Categories=Network;InstantMessaging;
StartupWMClass=DeepSeek Desktop
EOL

# Create launcher script
cat > ${PACKAGE_NAME}/usr/local/bin/${PACKAGE_NAME} <<EOL
#!/bin/bash
cd /opt/${PACKAGE_NAME}
python3 main.py
EOL
chmod +x ${PACKAGE_NAME}/usr/local/bin/${PACKAGE_NAME}

# Create control file
cat > ${PACKAGE_NAME}/DEBIAN/control <<EOL
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: all
Maintainer: Your Name <your@email.com>
Depends: python3, python3-pyqt5, python3-pyqt5.qtwebengine
Description: DeepSeek Desktop Client
 A cross-platform desktop client for DeepSeek chat.
EOL

# Set permissions
find ${PACKAGE_NAME} -type d -exec chmod 755 {} \;
find ${PACKAGE_NAME} -type f -exec chmod 644 {} \;
chmod +x ${PACKAGE_NAME}/usr/local/bin/${PACKAGE_NAME}

# Build the package
dpkg-deb --build ${PACKAGE_NAME}

# Clean up (optional)
# rm -rf ${PACKAGE_NAME}

echo "Package built: ${PACKAGE_NAME}_${VERSION}_all.deb"