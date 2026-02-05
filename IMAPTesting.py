from imaplib import IMAP4_SSL  # 必须使用 SSL
import datetime

# 保持你的日期逻辑不变
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
now = datetime.datetime.now()
imap_date = f"{now.day:02d}-{months[now.month-1]}-{now.year}"

# 使用 SSL 连接
imapOBJ = IMAP4_SSL("imap.gmail.com")
imapOBJ.login("stephen.xuxiangcheng@gmail.com", "wslw whry unvx kkfw")

# 检查 select 是否成功
status_select, data = imapOBJ.select("INBOX")
if status_select == 'OK':
    # 只有这里才是 SELECTED 状态
    status, email_ids = imapOBJ.search(None, f'SINCE "{imap_date}"')
    print(f"Search Status: {status}")
    print(f"Email IDs: {email_ids}")
    
    # 只有选中了才需要 close
    imapOBJ.close()
else:
    print(f"进入收件箱失败，服务器返回: {data}")

imapOBJ.logout()