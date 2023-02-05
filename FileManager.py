import os
import json
import re


class FileManager:
    def __init__(self) -> None:
        self.__path = "."

    def _replace_all_videos(self):
        _index_list = self.__index_all_videos_from_list(f"{self.__path}/online_video_list.txt")
        _file_list = self.list_files(f"{self.__path}")
        _id_list = list(map(self.__extract_video_id, _file_list))

        for index, id in enumerate(_id_list):
            if id =="":continue
            if id in _index_list:
                start = _file_list[index].find("[")
                end = _file_list[index].find("]")
                file_name = _file_list[index][start:end+1]
                if int(file_name.replace("]","").replace("[","")) == _index_list[id]:
                    continue
                new_name = _file_list[index].replace(file_name, f"[{_index_list[id]}]")
                os.rename(f"{_file_list[index]}", f"{new_name}")
                print(f"renamed:{_file_list[index]}->{new_name}")

    def _delete_duplicate(self):
        dictList = {}
        _file_list = self.list_files(f"{self.__path}")
        _id_list = list(map(self.__extract_video_id, _file_list))
        for index, id in enumerate(_id_list):
            if id == "":continue
            if id in dictList:
                os.remove(_file_list[index])
                print(f"removed:{_file_list[index]}")
            dictList.update({id: _file_list[index]})

    def __index_all_videos_from_list(self, video_list):
        youtube_index = {}
        with open(video_list, "r") as f:
            lines = f.readlines()
            for line in lines:
                if self.__is_json(line) :
                    line_to_json = json.loads(line)
                    youtube_index.update({line_to_json["id"]: line_to_json["n_entries"]-line_to_json["playlist_index"]-1})
        return youtube_index

    def list_files(self, folder_path):
        file_list = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    file_list.append(file_path)
        return file_list

    def __is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError as e:
            return False
        return True

    def __extract_video_id(self, video_url):
        start = video_url.rfind("[")+1
        end = video_url.rfind("]")
        video_id = video_url[start:end]
        if video_id == video_url:
            return ""
        if ".DS_Store" in video_id:return ""
        if "@eaDir" in video_id:return ""
        result = re.search(r'[a-zA-Z0-9-_]{11}$', video_id)
        if result != None:
            if result.span().index(11) == 1:
                return video_url[start:end]
            else:
                return ""
        else:
            return ""

    def delete_old_formate():
        cache_video = os.listdir(f".")
        delete_list = []
        for video in cache_video:
            if "].mp4" in video:
                pass
            else:
                delete_list.append(video)
        for video in delete_list:
            if ".mp4" in video:
                os.remove(video)


if __name__ == '__main__':
    fm = FileManager()
    # fm._replace_all_videos()
    fm._delete_duplicate()
