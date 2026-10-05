class DownloadCancelled(BaseException):
    """사용자가 다운로드 중지를 눌러 전송을 끊었을 때.

    Exception이 아니라 BaseException이라, 파일 루프의 except Exception이
    이 신호를 삼키고 다음 파일을 받지 않는다.
    """


class FileURLRetrievalError(Exception):
    pass


class FolderContentsMaximumLimitError(Exception):
    pass
