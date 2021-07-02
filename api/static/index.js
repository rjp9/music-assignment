function validateEmail(email) {
    return /[^@]+@[^@]+\.[^@]+/.test(email);
}

function downloadAssignment() {
    const option = document.querySelector('input[name="option"]:checked').value;
    const email = document.getElementById('email').value;
    const status = document.getElementById('download-status');
    if (!validateEmail(email)) {
        alert('Please enter a valid email!');
        return;
    }
    data = JSON.stringify({option: option, email: email})
    var req = new XMLHttpRequest();
    req.open("POST", "/api/download", true);
    req.setRequestHeader('Content-Type', 'application/json');
    req.responseType = "blob";
    // req.onreadystatechange = () => {
    //     if (req.readyState === 4) {
    //         status.innerHTML = 'Success!'
    //     } else {
    //         status.innerHTML = 'Downloading...'
    //     }
    // }

    // req.onprogress = (e) => { console.log(e); }
    req.onload = function (event) {
        if (req.status == 200) {

            if(req.response.type === 'application/pdf') {
                const header = req.getResponseHeader('content-disposition')
                const filename = /filename=(assignment\d+.pdf)/.exec(header)[1];
                var blob = req.response;
                var link = document.createElement('a');
                link.href = window.URL.createObjectURL(blob);
                link.download = filename;
                link.click();
                window.location.replace('/thanks');
            } else {
                req.response.text()
                .then(t => alert(JSON.parse(t).message));
            }
        }
    };
    const body = JSON.stringify({option: option, email: email});
    req.send(body);
}


function validateFields() {
    console.log('here');

    try {
        const univ = document.querySelector('input[name="univ"]:checked').value;
        const years = document.getElementById("years").value;
        const inst_diff = document.querySelector('input[name="inst"]:checked').value;
        const hymn_diff = document.querySelector('input[name="hymn-diff"]:checked').value;
        const hymn_fam = document.querySelector('input[name="hymn-fam"]:checked').value;
        const jazz_diff = document.querySelector('input[name="jazz-diff"]:checked').value;
        const jazz_fam = document.querySelector('input[name="jazz-fam"]:checked').value;
        const time =document.getElementById("time").value;
        const feedback = document.getElementById("feedback-text").value;
        console.log([univ, years, inst_diff, hymn_diff, hymn_fam, jazz_diff, jazz_fam, time, feedback])
        return true;
    } catch {
        alert("Please complete all required fields!");
        return false;
    }
  

}

function clicked() {
    const result = validateFields();
    if (result === false) {
        return;
    }
    const email = document.getElementById('email').value;
    if (!validateEmail(email)) {
        alert('Please enter a valid email first!');
        return;
    }
    document.getElementById('file').click();
}


function uploadAssignment(e) {

    const univ = document.querySelector('input[name="univ"]:checked').value;
    const years = document.getElementById("years").value;
    const inst_diff = document.querySelector('input[name="inst"]:checked').value;
    const hymn_diff = document.querySelector('input[name="hymn-diff"]:checked').value;
    const hymn_fam = document.querySelector('input[name="hymn-fam"]:checked').value;
    const jazz_diff = document.querySelector('input[name="jazz-diff"]:checked').value;
    const jazz_fam = document.querySelector('input[name="jazz-fam"]:checked').value;
    const time = document.getElementById("time").value;
    const feedback = document.getElementById("feedback-text").value;

    const status = document.getElementById('download-status');
    const email = document.getElementById('email').value;
    const data = new FormData();
    const pdf = e.files[0];
    if (pdf === undefined) {
        return;
    }

    data.append("univ", univ);
    data.append("years", years);
    data.append("inst_diff", inst_diff);
    data.append("hymn_diff", hymn_diff);
    data.append("hymn_fam", hymn_fam);
    data.append("jazz_diff", jazz_diff);
    data.append("jazz_fam", jazz_fam);
    data.append("time", time);
    data.append("feedback", feedback);

    data.append("email", email);
    data.append("pdf", pdf);
    const xhr = new XMLHttpRequest();
    // xhr.onload = () => {
    //     if (xhr.status === 4
    //     xhr.response.text().then(t => {
    //         console.log(t);
    //         status.innerHTML = t;
    //         alert(JSON.parse(t).message);
    //     });
    // };
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            let message;
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                message = result.message;
                if (result.status === 'success') {
                    status.innerHTML = message;
                    window.location.replace('/success');
                    return;
                }
            } else {
                console.log('here');
                message = 'Something went wrong :(. Please contact reedperkins@byu.edu for assistance.';
            }
            status.innerHTML = message;
            alert(message);
        } else {
            status.innerHTML = 'Uploading...';
        }
    }; 
    xhr.open('POST', '/api/upload', true);
    xhr.send(data);
}