FROM mcr.microsoft.com/devcontainers/dotnet:9.0

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION="22.18.0"

# Install Node.js 22.18.0, Python 3.11, and GitHub CLI using a single apt transaction
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    ARCH="$(dpkg --print-architecture)" \
    && case "${ARCH}" in \
        amd64) NODE_DISTRO="linux-x64" ;; \
        arm64) NODE_DISTRO="linux-arm64" ;; \
        *) echo "Unsupported architecture: ${ARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg status=none \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends git python3 python3-pip python3-venv gh xz-utils \
    && curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-${NODE_DISTRO}.tar.xz" -o node.tar.xz \
    && mkdir -p /usr/local/lib/nodejs \
    && tar -xJf node.tar.xz -C /usr/local/lib/nodejs \
    && rm node.tar.xz \
    && ln -sf /usr/local/lib/nodejs/node-v${NODE_VERSION}-${NODE_DISTRO}/bin/node /usr/local/bin/node \
    && ln -sf /usr/local/lib/nodejs/node-v${NODE_VERSION}-${NODE_DISTRO}/bin/npm /usr/local/bin/npm \
    && ln -sf /usr/local/lib/nodejs/node-v${NODE_VERSION}-${NODE_DISTRO}/bin/npx /usr/local/bin/npx \
    && export PATH="/usr/local/lib/nodejs/node-v${NODE_VERSION}-${NODE_DISTRO}/bin:$PATH" \
    && npm config set prefix /usr/local \
    && npm install -g npm@latest \
    && pip3 install --no-cache-dir --upgrade pip \
    && node --version \
    && npm --version \
    && python3 --version \
    && pip3 --version \
    && [ -e /usr/local/bin/python ] || ln -s /usr/bin/python3 /usr/local/bin/python \
    && python --version \
    && apt-get clean \
    && rm -rf /tmp/*

# Install Azure CLI
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/microsoft.gpg > /dev/null \
    && AZ_REPO=$(. /etc/os-release && echo $VERSION_CODENAME) \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | tee /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends azure-cli \
    && az version \
    && apt-get clean \
    && rm -rf /tmp/*

# Install Azure Developer CLI (azd)
RUN curl -fsSL https://aka.ms/install-azd.sh | bash \
    && azd version

# Install Azure Functions Core Tools v4 and Azurite
ENV PATH="/usr/local/bin:$PATH"
RUN npm install -g azure-functions-core-tools@4 --unsafe-perm true --force \
    && npm install -g azurite \
    && func --version \
    && azurite --version

# Set the working directory
WORKDIR /workspace

# Ensure workspace ownership and permissions for vscode user
RUN chown -R vscode:vscode /workspace \
    && chmod -R u+rwX,go+rX /workspace

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone