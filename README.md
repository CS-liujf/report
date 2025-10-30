## 简介

自动化快速登记听报告记录。

## 如何使用

1. 安装 `icalendar`包

   ```bash
   pip install icalendar
   # 或
   conda install icalendar
   ```

2. 创建空文件夹，将 `main.py`放置其中

3. 下载邮件到该文件夹

   电脑端登录校园邮箱，搜索seminar邮件，下载已参与的邮件。下载方式：上方菜单栏点击”更多“

4. 设置学号

   编辑 `main.py`中的学号

   ```python
   # 使用示例
   if __name__ == "__main__":
      student_id = '学号'
      main(student_id)
   ```

5. 在该文件夹内运行 `main.py`

   若一切正常，会产生一个名为`output.js`的文件

6. 复制`output.js`的内容

7. 进入研究生系统里的“听报告登记”，按F12打开开发工具

8. 粘贴所复制的内容于控制台并运行

   运行方式为压enter键

9. 手动刷新该界面

## TODO

当前需要python，并且非图形化界面，操作略有不便

- [ ] 创建一个网页不再依赖python，图形化操作
