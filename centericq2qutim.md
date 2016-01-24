# (English) centericq2qutim.py
This utility convert the CenterICQ message history to the qutIM message
history. Please, do not use the qutIM working copy as the output directory. It
may damage the your message history. Just select an empty directory as the
output directory.

## Changelog
### v0.1.0
- initial version

## Usage:
```bash
usage: centericq2qutim.py [-h] [--version] [--verbose] [--uin UIN] [--jid JID]
                          --src SRC --dst DST

optional arguments:
  -h, --help  show this help message and exit
  --version   show program's version number and exit
  --verbose   print various debugging information
  --uin UIN   set your UIN to convert the ICQ message history
  --jid JID   set your JID to convert the JABBER message history
  --src SRC   the input directory with the CenterICQ message history
  --dst DST   the output directory. WARNING: do not use the qutIM working copy
              as the output directory. It may damage the your message history.
              Just select an empty directory
```


# (Русский) centericq2qutim.py
Данная утилита преобразует историю сообщений CenterICQ в историю сообщений qutIM.
Пожалуйста, не используйте в качестве выходной директории рабочий каталог qutIM.
Это может повредить вашу историю сообщений. Лучшим решением будет выбрать 
пустую выходную директорию.

## История изменений
### v0.1.0
- первоначальная версия

## Использование:
```bash
usage: centericq2qutim.py [-h] [--version] [--verbose] [--uin UIN] [--jid JID]
                          --src SRC --dst DST

аргументы запуска:
  -h, --help  показать это сообщение и выйти
  --version   показать версию программы и выйти
  --verbose   показывать различную отладочную информацию
  --uin UIN   установите ваш UIN для преобразования истории ICQ
  --jid JID   установите ваш JID для преобразования истории JABBER
  --src SRC   входная директория с историей сообщений CenterICQ
  --dst DST   выходная директория. Предупреждение: не используйте 
              в качестве выходной директории рабочий каталог qutIM.
              Это может повредить вашу историю сообщений. 
              Лучшим решением будет выбрать пустую выходную директорию
```
