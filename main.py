from icalendar import Calendar, Component
from email import policy
from email.parser import BytesParser
import re
from dataclasses import asdict, dataclass
from pathlib import Path
import json
from datetime import datetime


@dataclass
class SeminarInfoForm:
    WID: str = ""
    SHZT_DISPLAY: str = ""
    SHZT: str = "0"
    TBLX: str = ""
    XH: str = ""
    FJ: str = ""
    XNXQ_DISPLAY: str = ""
    XNXQ: str = ""
    BGMC: str = ""
    BGSJ: str = ""
    BGDD: str = ""
    ZJR: str = ""
    SFSYYY_DISPLAY: str = "是"
    SFSYYY: str = "1"


@dataclass
class SeminarInfo:
    date: str = ''
    location: str = ''
    spearker: str = ''
    subject: str = ''


@dataclass
class CalendarInfo:
    date_str = ''
    location = ''


def ParseEml(file_path: str) -> SeminarInfo:

    def SanitizeSubject(raw_subject_str: str) -> str:
        cleaned = re.sub(r'^\[[^\]]*\]\s*', '', raw_subject_str)
        return cleaned

    def ExtractSpeakerFromContent(text: str) -> str:
        """
        从邮件正文中把演讲者提取出来
        """
        speaker: str = ''

        # 提取主讲人: Speaker: Grzegorz Litak
        speaker_match = re.search(r'^(?:Speaker|演讲者):\s*(.+)$', text,
                                  re.MULTILINE | re.IGNORECASE)

        if speaker_match:
            speaker = speaker_match.group(1).strip()

        return speaker

    def ExtractDateAndLocationFromCalendar(calendar_str: str) -> CalendarInfo:
        calInfo = CalendarInfo()
        cal = Calendar.from_ical(calendar_str)
        for component in cal.walk():
            if component.name == "VEVENT":
                start_time = component.get('dtstart').dt  # 开始时间
                date_str = start_time.strftime("%Y-%m-%d")  # 直接格式化

                location = component.get('location',
                                         '未指定地点').to_ical().decode('utf-8')
                calInfo.date_str = date_str
                calInfo.location = location

        return calInfo

    info = SeminarInfo()

    with open(file_path, 'rb') as f:  # 注意：以二进制模式打开
        msg = BytesParser(policy=policy.default).parse(f)

    raw_subject_str: str = msg.get('Subject', '')
    info.subject = SanitizeSubject(raw_subject_str)

    calendar_str: str = ''
    body: str = ''

    #获取邮件正文
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get("Content-Disposition", ""))
        # 检查MIME类型是否为日历（iCalendar）
        if content_type in ['text/calendar', 'application/ics']:
            calendar_str = part.get_payload(decode=True)  # type: ignore

        elif 'attachment' in content_disposition:
            continue

        elif content_type == "text/plain" and "attachment" not in content_disposition:
            # 获取纯文本正文
            body = part.get_content()

    #提取日历中的时间和地点
    cal_info = ExtractDateAndLocationFromCalendar(calendar_str)
    info.date, info.location = cal_info.date_str, cal_info.location

    # 从邮件正文获取演讲者
    speaker = ExtractSpeakerFromContent(body)
    info.spearker = speaker

    return info


@dataclass
class AcademicTerm:
    term_str: str
    term_code: str


def GenerateJsFile(info_list: list[SeminarInfo], student_id: str):

    def GetAcademicTerm(date_str: str) -> AcademicTerm:
        """
        根据日期字符串（格式：YYYY-MM-DD）返回对应的学年学期信息
        
        规则：
            - 9月 ~ 1月   → "y-y+1学年 第一学期", 编码: y1
            - 7月 ~ 8月    → "(y-1)-y学年 第三学期", 编码: (y-1)3
            - 2月 ~ 6月    → "(y-1)-y学年 第二学期", 编码: (y-1)2
        
        参数:
            date_str (str): 日期字符串，如 "2025-09-21"
        
        返回:
            tuple[学期描述, 学期编码]
        """
        # 解析日期
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            y = dt.year
            m = dt.month
        except ValueError as e:
            raise ValueError(f"日期格式错误，应为 YYYY-MM-DD: {date_str}") from e

        if m >= 9 or m < 2:
            # 9月到12月：第一学期
            term_str = f"{y}-{y+1}学年 第一学期"
            term_code = y * 10 + 1  # y1
        elif m in [7, 8]:
            # 7月和8月：第三学期
            term_str = f"{y-1}-{y}学年 第三学期"
            term_code = (y - 1) * 10 + 3  # y3
        else:
            # 1月到6月：第二学期
            term_str = f"{y-1}-{y}学年 第二学期"
            term_code = (y - 1) * 10 + 2  # (y-1)2

        return AcademicTerm(term_str, str(term_code))

    form_list: list[SeminarInfoForm] = []
    for info in info_list:
        academic_term = GetAcademicTerm(info.date)
        form = SeminarInfoForm()
        form.XH = student_id

        form.XNXQ_DISPLAY = academic_term.term_str
        form.XNXQ = academic_term.term_code

        form.BGMC = info.subject
        form.BGSJ = info.date
        form.BGDD = info.location
        form.ZJR = info.spearker
        form_list.append(form)

    json_str = json.dumps([asdict(d) for d in form_list],
                          ensure_ascii=False,
                          indent=2)

    # 写入json文件
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump([asdict(d) for d in form_list],
                  f,
                  ensure_ascii=False,
                  indent=2)
    try:
        with open('./index.js', 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换：const seminarInfoArr = [] 为 const seminarInfoArr = [ ... ]
        new_content = content.replace('const seminarInfoArr = []',
                                      f'const seminarInfoArr = {json_str}', 1)

        # 写回文件
        with open('./output.js', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("✅ JS 文件已成功生成！")

    except FileNotFoundError:
        print(f"❌ 文件未找到: index.js")
    except Exception as e:
        print(f"❌ 发生错误: {e}")


def main(student_id: str):
    # 获取当前脚本所在的目录
    script_dir = Path(__file__).parent.resolve()

    print(f"当前脚本所在目录: {script_dir}")

    # 获取该目录下所有 .eml 文件
    eml_files = [
        f for f in script_dir.iterdir()
        if f.is_file() and f.suffix.lower() == '.eml'
    ]

    file_path_list: list[str] = []
    # 输出结果
    if eml_files:
        for eml_file in eml_files:
            file_path_list.append(eml_file.name)
    else:
        raise Exception("未找到任何 .eml 文件")

    info_list = [ParseEml(file_path) for file_path in file_path_list]
    GenerateJsFile(info_list, student_id)


# 使用示例
if __name__ == "__main__":
    student_id = '学号'
    main(student_id)
