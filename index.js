// 发送 POST 请求
try {
    // 用json中的数组替换该空数组
    const seminarInfoArr = []
    const postRequest = async (seminarInfo) => {
        const paramJson = JSON.stringify(seminarInfo);
        const formData = new URLSearchParams();
        formData.append('paramJson', paramJson);
        await fetch('https://graduate.shanghaitech.edu.cn/gsapp/sys/jzxxtjapp/tbgdj/save.do', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        })
    }
    const postReqArr = seminarInfoArr.map((seminarInfo) => postRequest(seminarInfo))
    Promise.all(postReqArr)
} catch (e) {
    console.log(e)
}
