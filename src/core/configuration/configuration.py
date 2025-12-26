import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict


class EnvConfig(TypedDict, total=False):
    NODE_ENV: Literal["development", "production", "test"]
    PORT: int

    DATABASE_ENGINE: str
    TZ: str
    HF_TOKEN: str


@dataclass
class EnvVarSchema:
    required: bool
    type: type
    default: Any = None


class Configuration:
    _instance: "Configuration | None" = None

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._env_schema: dict[str, EnvVarSchema] = {
            "NODE_ENV": EnvVarSchema(required=False, type=str, default="development"),
            "PORT": EnvVarSchema(required=False, type=int, default=8000),
            "DATABASE_URL": EnvVarSchema(required=True, type=str),
            "DATABASE_ENGINE": EnvVarSchema(required=False, type=str, default="mongodb"),
            "UPLOADS_PATH": EnvVarSchema(required=False, type=str, default="uploads"),
            "FILE_STORAGE_VENDOR": EnvVarSchema(required=False, type=str, default="local"),
            "CHUNK_SIZE": EnvVarSchema(required=False, type=int, default=2048),
            "CHUNK_OVERLAP": EnvVarSchema(required=False, type=int, default=200),
            "CHUNK_STRATEGY": EnvVarSchema(required=False, type=str, default="vanilla"),
            "TZ": EnvVarSchema(required=False, type=str, default="America/Bogota"),
            "HF_TOKEN": EnvVarSchema(required=True, type=str),
            "LOG_LEVEL": EnvVarSchema(required=False, type=str, default="INFO"),
            "TEMPORAL_HOST": EnvVarSchema(required=True, type=str),
            "EMBEDDING_MODEL_CHUNK": EnvVarSchema(required=False, type=str, default="all-MiniLM-L6-v2"),
            "EMBEDDING_MODEL": EnvVarSchema(required=False, type=str, default="vanilla"),
        }
        self._load_env_file()
        self._validate_config()

    def __new__(cls) -> "Configuration":
        if cls._instance is None:
            cls._instance = super(Configuration, cls).__new__(cls)
        return cls._instance

    def get(self, key: str) -> Any:
        return self._config.get(key)

    def _validate_config(self) -> None:
        missing_required: list[str] = []

        for key, schema in self._env_schema.items():
            raw_value = os.getenv(key)

            if not raw_value:
                if schema.required:
                    missing_required.append(key)
                    continue
                if schema.default is not None:
                    self._config[key] = schema.default
                    continue

            if raw_value:
                parsed_value = self._parse_value(raw_value, schema.type)
                self._config[key] = parsed_value

        if missing_required:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_required)}")

    def _parse_value(self, value: str, value_type: type) -> Any:
        if value_type == int:
            try:
                return int(value)
            except ValueError:
                raise ValueError(f"Invalid number value: {value}")
        if value_type == bool:
            return value.lower() in ("true", "1", "yes")
        return value

    def _load_env_file(self) -> None:
        env_file = ".env.test" if os.getenv("NODE_ENV") == "test" else ".env"
        env_path = Path.cwd() / env_file

        if not env_path.exists():
            print(f"Warning: {env_file} file not found at {env_path}")
            return

        try:
            content = env_path.read_text(encoding="utf-8")
            self._parse_env_content(content)
        except Exception as error:
            print(f"Error reading {env_file}: {error}")

    def _parse_env_content(self, content: str) -> None:
        env_vars: dict[str, str] = {}

        for line in content.split("\n"):
            trimmed = line.strip()

            if not trimmed or trimmed.startswith("#"):
                continue

            if "=" not in trimmed:
                continue

            key, _, value = trimmed.partition("=")
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]

            env_vars[key] = value

        # Only set if not already in environment
        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value


config = Configuration()
