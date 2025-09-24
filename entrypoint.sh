#!/bin/sh
set -eu

APP_USER=${APP_USER:-app}
APP_GROUP=${APP_GROUP:-app}
APP_UID=${APP_UID:-}
APP_GID=${APP_GID:-}
APP_HOME=${APP_HOME:-/home/${APP_USER}}
APP_PATH=${APP_PATH:-/app}

DEFAULT_UID=1000
DEFAULT_GID=1000

detect_uid_gid() {
    target="$1"

    if [ -z "$target" ] || [ ! -e "$target" ]; then
        return 1
    fi

    if command -v stat >/dev/null 2>&1; then
        if stats=$(stat -c '%u %g' "$target" 2>/dev/null); then
            printf '%s\n' "$stats"
            return 0
        fi
        if stats=$(stat -f '%u %g' "$target" 2>/dev/null); then
            printf '%s\n' "$stats"
            return 0
        fi
    fi

    return 1
}

maybe_detect_uid_gid() {
    detect_target="$1"

    if detection=$(detect_uid_gid "$detect_target"); then
        set -- $detection
        detected_uid="$1"
        detected_gid="$2"

        if [ -n "$detected_uid" ]; then
            if [ -z "$APP_UID" ] || [ "$APP_UID" = "$DEFAULT_UID" ]; then
                APP_UID="$detected_uid"
            fi
        fi
        if [ -n "$detected_gid" ]; then
            if [ -z "$APP_GID" ] || [ "$APP_GID" = "$DEFAULT_GID" ]; then
                APP_GID="$detected_gid"
            fi
        fi
    fi
}

maybe_detect_uid_gid "$APP_PATH"

APP_UID=${APP_UID:-$DEFAULT_UID}
APP_GID=${APP_GID:-$DEFAULT_GID}

if [ "$(id -u)" -eq 0 ]; then
    if [ "$APP_GID" != "0" ]; then
        if ! getent group "$APP_GROUP" >/dev/null 2>&1; then
            groupadd --gid "$APP_GID" "$APP_GROUP"
        else
            CURRENT_GID="$(getent group "$APP_GROUP" | cut -d: -f3)"
            if [ "$CURRENT_GID" != "$APP_GID" ]; then
                groupmod -o -g "$APP_GID" "$APP_GROUP"
            fi
        fi
    else
        APP_GROUP=root
    fi

    if [ "$APP_UID" != "0" ]; then
        if ! id "$APP_USER" >/dev/null 2>&1; then
            useradd --uid "$APP_UID" --gid "$APP_GID" --home-dir "$APP_HOME" --shell /bin/bash --create-home "$APP_USER"
        else
            CURRENT_UID="$(id -u "$APP_USER")"
            if [ "$CURRENT_UID" != "$APP_UID" ]; then
                usermod -o -u "$APP_UID" "$APP_USER"
            fi
            usermod -g "$APP_GID" "$APP_USER"
        fi
        mkdir -p "$APP_HOME"
        chown -R "$APP_UID:$APP_GID" "$APP_HOME" 2>/dev/null || true
    else
        APP_USER=root
        APP_HOME=/root
    fi

    mkdir -p "$APP_PATH"
    chown -R "$APP_UID:$APP_GID" "$APP_PATH" 2>/dev/null || true

    if [ "$APP_UID" = "0" ]; then
        exec "$@"
    else
        exec gosu "$APP_USER" "$@"
    fi
else
    exec "$@"
fi
