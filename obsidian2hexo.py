import os
import re
import sys
import traceback
import subprocess
import yaml
import shutil
from datetime import datetime
from util.logger import Logger
from util.tools import get_cur_timestr

logger = Logger(__file__)
logger.set_handler("file")


class Note():
    def __init__(self, root_dir, file_path, share_tag, resource, note_index):
        self.root_dir = root_dir
        self.file_path = file_path
        self.share_tag = share_tag
        self.resource = resource
        self.note_index = note_index
        self.file_name = self.get_file_name()
        self.content = self.get_content()
        self.tags = self.get_tags()
        self.is_share = self.check_share()
        self.images = self.get_images()
        self.files = self.get_files()
        self.links = self.get_links()
        self.real_path = self.get_real_path()
        self.depth = self.get_depth()
        self.commits = self.get_git_commits()
        self.create_date = self.get_create_date()
        self.last_date = self.get_last_date()

    def get_content(self):
        with open(self.file_path, "r", encoding='utf-8') as f:
            first_line = f.readline()
            content = f.read()
            content.replace(first_line, '')
            return content

    def get_tags(self):
        first_line = ""
        with open(self.file_path, "r", encoding='utf-8') as f:
            first_line = f.readline()

        pattern_tag = '#\S*'
        tags = []
        all_tag = re.compile(pattern_tag).findall(first_line)
        self.is_share = False
        for tag in all_tag:
            if f"#{share_tag}" == tag:
                self.is_share = True
                continue
            tag = tag.replace('#', '')
            if '/' in tag:
                tags.extend(tag.split('/'))
                continue
            tags.append(tag)
        return set(tags)

    def check_share(self):
        return self.is_share

    def get_links(self):
        pattern_link = '(?<!\S)\[\[.*\]\]'
        links = re.compile(pattern_link).findall(self.content)
        link_files = []
        for link in links:
            link_file = link.replace("[[", "")
            link_file = link_file.replace("]]", "")
            link_file = link_file.replace("/", os.sep)
            md_link = f"[[{link_file}]]"
            self.content = self.content.replace(link, md_link)
            link_files.append(link_file)
        return link_files

    def is_res_available(self, img):
        from_path = f"{self.resource}/{img}"
        if os.path.exists(from_path):
            return True
        return False

    def get_images(self):
        images = []

        pattern_image1 = '(?<!\S)!\[\[.*\]\]'
        res1 = re.compile(pattern_image1).findall(self.content)
        for link in res1:
            image = link.replace("![[", "")
            image = image.replace("]]", "")
            if '|' in image:
                image = image.split('|')[0].strip()
            if self.is_res_available(image):
                images.append(image)
                image_link = f"![](/images/{image})"
                self.content = self.content.replace(link, image_link)

        pattern_image2 = '(?<!\S)!\[.*\]\(.*\)'
        res2 = re.compile(pattern_image2).findall(self.content)
        for link in res2:
            if 'http' in link:
                continue
            front = re.search("(?<!\S)!\[.*\]\(", link).group()
            image = link.replace(front, "")
            image = image.replace(")", "")
            if self.is_res_available(image):
                images.append(image)
                image_link = f"![](/images/{image})"
                self.content = self.content.replace(link, image_link)

        return images

    def get_files(self):
        files = []
        pattern_file = '(?<!\S)\[.*\]\(.*\)'
        res = re.compile(pattern_file).findall(self.content)
        for link in res:
            if 'http' in link:
                continue
            front = re.search("(?<!\S)\[.*\]\(", link).group()
            file = link.replace(front, "")
            file = file.replace(")", "")
            if self.is_res_available(file):
                files.append(file)
                image_link = f"[{file}](/download/{file})"
                self.content = self.content.replace(link, image_link)

        return files

    def get_real_path(self):
        real_path = self.file_path.replace(self.root_dir, '')
        return real_path

    def get_depth(self):
        depth = 0
        for c in self.real_path:
            if c == os.sep or c == '/':
                depth += 1
        return depth

    def get_file_name(self):
        filepath, filename = os.path.split(self.file_path)
        name, extension = os.path.splitext(filename)
        return name

    def get_git_commits(self):
        return get_commits(self.root_dir, self.file_path)

    def get_create_date(self):
        if len(self.commits) > 0:
            oldest_commit = self.commits[-1]
            return convert_git_date(oldest_commit)
        return get_cur_timestr()

    def get_last_date(self):
        if len(self.commits) > 0:
            last_commit = self.commits[0]
            return convert_git_date(last_commit)
        return get_cur_timestr()

    def reset_link(self, link, link_url):
        self.content = self.content.replace(link, link_url)

    def get_metadata(self):
        title = self.file_name
        date = self.create_date

        categories = []
        paths = self.real_path.split(os.sep)
        for path in paths:
            if path == '' or path.endswith('.md'):
                continue
            categories.append(path)

        tags = []
        for tag in self.tags:
            tags.append(tag)

        metadata = f"""---
title: {title}
date: {date}
categories: {categories}
tags: {tags}
---\n
"""
        return metadata

    def get_full_content(self):
        self.content = self.content.replace("??\n", "\n")
        self.content = self.content.replace("```run-", "```")
        full = self.get_metadata() + self.content
        return full


def get_cur_file_name():
    """ 获取当前文件名字, 不带后缀 """
    cur_file_name = os.path.basename(os.path.realpath(sys.argv[0]))
    if '.' in cur_file_name:
        cur_file_name = cur_file_name.split('.')[0]
    return cur_file_name


def get_full_relative_path(relative_path):
    """ 生成基于当前脚本路径的相对路径. """
    cur_file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    full_relative_path = f"{cur_file_path}/{relative_path}"
    return full_relative_path


def load_config():
    """ 加载自动运行配置 """
    file_name = get_cur_file_name()
    config_path = f"{file_name}.yml"
    with open(get_full_relative_path(config_path), 'r', encoding='utf-8') as file:
        config = file.read()
        return yaml.safe_load(config)


def is_exclude(exludes, path):
    if not path.endswith('.md'):
        return True

    for exclude in exludes:
        if exclude in path:
            return True
    return False


def get_all_notes(root_dir, excludes, share_tag, resource):
    try:
        notes = []
        share_notes = []
        note_index = 0
        for root, dirs, files in os.walk(root_dir):
            # 输出所有的文件夹路径
            for file in files:
                file_path = os.path.join(root, file)
                if is_exclude(excludes, file_path):
                    continue
                logger.info(f"processing note: {note_index} {file_path}")
                note_index += 1
                note = Note(root_dir, file_path, share_tag, resource, note_index)
                notes.append(note)
                if note.check_share():
                    share_notes.append(note)
                    logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> shared note: {file_path}")
    except Exception as e:
        logger.error(f'get_all_notes Exception:{e} trackback:{traceback.format_exc()}')

    return notes, share_notes


def get_link_url(notes, link):
    for note in notes:
        note_link = f"[[{note.file_name}]]"
        if note_link == link:
            '../'


def process_links(notes, share_notes):
    for note in share_notes:
        for link in note.links:
            link_url = get_link_url(notes, link)
            note.reset_link(link, link_url)


def get_commits(repo_path, file_full_path):
    os.chdir(repo_path)

    order = ['git', 'log']
    if file_full_path is not None:
        order = f'git log -- "{file_full_path}"'

    output = subprocess.check_output(order, stderr=subprocess.STDOUT, creationflags=0x08000000)
    lines = output.splitlines()
    commits = []
    current_commit = {}

    def save_current_commit():
        title = current_commit['message'][0]
        message = current_commit['message'][1:]
        if message and message[0] == '':
            del message[0]
        current_commit['title'] = title
        current_commit['message'] = '\n'.join(message)
        commits.append(current_commit)

    for l in lines:
        line = l.decode('utf-8')
        if not line.startswith(' '):
            if line.startswith('commit '):
                if current_commit:
                    save_current_commit()
                    current_commit = {}
                current_commit['hash'] = line.split('commit ')[1]
            else:
                try:
                    key, value = line.split(':', 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            leading_4_spaces = re.compile('^    ')
            current_commit.setdefault('message', []).append(leading_4_spaces.sub('', line))
    if current_commit:
        save_current_commit()
    return commits


def convert_git_date(commit):
    date = commit['date']
    datetime_object = datetime.strptime(' '.join(date.split(' ')[:-1]), '%a %b %d %H:%M:%S %Y')
    return datetime_object


def get_link_note(notes, link):
    for note in notes:
        if '#' in link:
            link = link.split('#')[0]

        if os.sep in link:
            if note.real_path == f"{os.sep}{link}.md":
                return note
        else:
            if note.file_name == link:
                return note


def gen_hexo_notes(notes, share_notes, path_to, resource):
    logger.info("********************************* gen_hexo_notes *********************************")
    posts_foler = f"{path_to}/source/_posts/"
    shutil.rmtree(posts_foler, ignore_errors=True)
    os.mkdir(posts_foler)
    for note in share_notes:
        logger.info(f"generate hexo note: {note.note_index} {note.file_name}")
        for img in note.images:
            from_path = f"{resource}/{img}"
            to_path = f"{path_to}/source/images/{img}"
            shutil.copyfile(from_path, to_path)
        for file in note.files:
            from_path = f"{resource}/{file}"
            to_path = f"{path_to}/source/download/{file}"
            shutil.copyfile(from_path, to_path)
        for link in note.links:
            link_note = get_link_note(notes, link)
            if link_note is not None:
                link_path = f"[{link_note.file_name}](../{link_note.note_index})"
                if '#' in link:
                    link_title = link.split('#')[-1]
                    link_path = f"[{link_note.file_name}](../{link_note.note_index}/#{link_title})"
                note.content = note.content.replace(f"[[{link}]]", link_path)
        note_path = f"{path_to}/source/_posts/{note.note_index}.md"
        with open(note_path, "w", encoding="utf-8") as wordFile:
            wordFile.write(note.get_full_content())


def replace_by_sep(source_path):
    source_path = source_path.replace("/", os.sep)
    return source_path


def deploy_hexo(hexo_path):
    """ 运行命令行 """
    logger.info("********************************* deploy_hexo *********************************")

    try:
        os.chdir(hexo_path)
        time_str = get_cur_timestr()
        order_arr = ["hexo clean", "hexo g", "hexo d", "git status", "git add .", "git commit -m " + '"' + 'note:update ' + time_str + '"', "git pull", "git push"]  # 创建指令集合
        for order in order_arr:
            output = subprocess.check_output(order, stderr=subprocess.STDOUT, shell=True, creationflags=0x08000000)
            lines = output.splitlines()
            for line in lines:
                logger.info(line.decode('utf-8'))
        logger.info("********************************* hexo deploy success! *********************************")
    except Exception as e:
        print(f"deploy_hexo Exception:{e} trackback:{traceback.format_exc()}")


if __name__ == "__main__":
    config = load_config()

    path_from = replace_by_sep(config['path_from'])
    path_to = replace_by_sep(config['path_to'])

    resource = replace_by_sep(config['resource'])
    excludes = config['exclude']
    exclude = []
    if excludes is not None:
        for e in excludes:
            exclude.append(replace_by_sep(e))
        exclude.append(resource)
    share_tag = config['share_tag']
    if share_tag is None:
        share_tag = 'share'
    interval = config['interval']
    if interval is None:
        interval = 1800

    logger.info(f"\npath_from:\t{path_from}\n"
                f"exclude:\t{exclude}\n"
                f"path_to:\t{path_to}\n"
                f"share_tag:\t{share_tag}\n"
                f"interval:\t{interval}\n")

    notes, share_notes = get_all_notes(path_from, exclude, share_tag, resource)
    gen_hexo_notes(notes, share_notes, path_to, resource)
    deploy_hexo(path_to)
