import datetime
from macnotesapp import NotesApp, Note

def get_unprocessed_apple_notes() -> list[Note]:
    """
    Apple純正メモアプリから「#処理済み」タグが付いていないメモを取得します。
    """
    notesapp = NotesApp()
    unprocessed_notes = [
        n for n in notesapp.notes()
        if "#処理済み" not in n.plaintext
    ]
    return unprocessed_notes

def mark_apple_note_as_processed(note: Note):
    """
    指定されたAppleメモに「#処理済み」タグを付与します。
    """
    try:
        # Noteオブジェクトのbodyプロパティを直接変更
        # bodyはHTML形式なので <br><br>#処理済み を追記する
        note.body += "<br><br>#処理済み"
        print(f"✅ Appleメモ「{note.name}」を処理済みにしました。")
    except Exception as e:
        print(f"❌ Appleメモ「{note.name}」の処理済みタグ付けに失敗しました: {e}")
