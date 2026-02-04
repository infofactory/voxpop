from .models import DownloadableFile

def load_files(request):
    files = DownloadableFile.objects.all()
    return {'files': files}