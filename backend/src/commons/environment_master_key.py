from enum import Enum


class EnvironmentMasterKey(Enum):
    """
    環境情報マスタのキーを管理する列挙型クラス。
    各キーは環境情報マスタテーブルに格納されるデータ項目を表します。
    """

    PROJECT_ID: str = "10000001"
    """
    プロジェクトID。
    プロジェクト全体の一意の識別子として使用されます。
    """

    VERSION: str = "10000002"
    """
    バージョン情報。
    アプリケーションやサービスの現在のバージョンを示します。
    """

    SECRET: str = "10000003"
    """
    シークレットキー。
    セキュリティ目的で使用される秘密情報を格納します。
    """

    MASTER_SHEET_ID: str = "10000004"
    """
    マスターシートID。
    環境情報が保存されているスプレッドシートの識別子。
    """

    USERS_SHEET_NAME: str = "10000005"
    """
    社員情報シート名。
    社員情報が記載されたスプレッドシートのシート名。
    """

    CATEGORY_SHEET_NAME: str = "10000006"
    """
    カテゴリ情報シート名。
    カテゴリ情報が記載されたスプレッドシートのシート名。
    """

    WHITE_LIST_SHEET_NAME: str = "10000007"
    """
    ホワイトリスト情報シート名。
    ホワイトリスト情報が記載されたスプレッドシートのシート名。
    """

    GOGGLE_API_USER_INFO_URL: str = "10000008"
    """
    Google APIのユーザー情報取得URL。
    OAuth2.0認証情報に基づいてユーザー情報を取得するためのエンドポイントURL。
    """

    CLOUD_FLARE_IP_LIST_IPV4: str = "10000009"
    """
    CloudflareのIPv4アドレスリスト。
    サービスのセキュリティやネットワーク設定に使用されます。
    """

    CLOUD_FLARE_IP_LIST_IPV6: str = "100000010"
    """
    CloudflareのIPv6アドレスリスト。
    サービスのセキュリティやネットワーク設定に使用されます。
    """

    @property
    def key(self) -> str:
        """
        キー名を取得します。

        Returns:
            str: 列挙型メンバーの名前（例: "PROJECT_ID"）。
        """
        return self.name

    @property
    def value(self) -> str:
        """
        キーに対応する値を取得します。

        Returns:
            str: 列挙型メンバーの値（例: "10000001"）。
        """
        return super().value  # type: ignore

    @classmethod
    def get_value_by_key(cls, key: str) -> str | None:
        """
        指定されたキー名に対応する値を取得します。

        Args:
            key (str): 環境情報マスタのキー名。

        Returns:
            str | None: 指定されたキー名に対応する値。キーが存在しない場合は`None`。
        """
        return next((item.value for item in cls if item.key == key), None)

    @classmethod
    def is_valid_key(cls, key: str) -> bool:
        """
        指定されたキー名が有効な環境情報マスタのキーかを確認します。

        Args:
            key (str): チェック対象のキー名。

        Returns:
            bool: 有効なキーであれば`True`、無効なキーであれば`False`。
        """
        return any(item.key == key for item in cls)
