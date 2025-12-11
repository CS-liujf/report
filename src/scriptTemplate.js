(async () => {
  try {
    const seminarInfoArr = [];
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
      });
    };
    const postReqArr = seminarInfoArr.map((seminarInfo) => postRequest(seminarInfo));
    await Promise.all(postReqArr);
  } catch (e) {
    console.log(e);
  }
})();