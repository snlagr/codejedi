let editor = CodeMirror.fromTextArea(document.querySelector('#editor'), {
    mode: 'python',
    lineNumbers: true,
    theme: "solarized light",
});

document.querySelector('#themeChange').addEventListener('change', (e) => {
    editor.setOption("theme", document.querySelector('#themeChange').value);
})

let current = 13;

document.querySelector('#increaseText').addEventListener('click', (e) => {
    current = current + 2;
    editor.getWrapperElement().style["font-size"] = current + "px";
    editor.refresh();
})

document.querySelector('#decreaseText').addEventListener('click', (e) => {
    current = current - 2;
    editor.getWrapperElement().style["font-size"] = current + "px";
    editor.refresh();
})

document.querySelector('#language').addEventListener('change', () => {
    let language = document.querySelector('#language').value;
    switch (language) {
        case 'python3':
            language = 'python';
            break;
        case 'cpp17':
            language = 'text/x-c++src';
            break;
        case 'nodejs':
            language = 'javascript';
            break;
        case 'java':
            language = 'text/x-java';
            break;
    }
    editor.setOption('mode', language);
})

// document.querySelector('#enterFullScreen').addEventListener('click', () => {
//     editor.setOption("fullScreen", true);
// })

document.querySelector('#runcode').addEventListener('click', () => {
    let script = editor.getValue();
    let stdin = document.querySelector('#customInput').value;
    let lang = document.querySelector('#language').value;
    if (lang == 'none') {
        document.querySelector('#customOut').innerHTML = "Custom Output...";
        swal("Wait!", "Please select a language first.", "warning");
        return;
    }
    let callURL = `${document.location.protocol}//${document.location.host}/runcode`;
    let loading_animation = `<div id="customLoad" class="fa-4x d-flex justify-content-center align-items-center"
    style="height: 100%; visibility: hidden;">
    <i class="fas fa-sync fa-spin"></i>
    </div>`;
    document.querySelector('#customOut').innerHTML = loading_animation;
    document.querySelector('#customLoad').style.visibility = "visible";
    axios.post(callURL, {
        "lang": lang,
        "script": script,
        "stdin": stdin,
    }).then(res => {
        document.querySelector('#customOut').innerHTML = res.data.output + loading_animation;
    });
});

document.querySelector('#submitcode').addEventListener('click', () => {
    let loading_animation = `<div id="customLoad" class="fa-4x d-flex justify-content-center align-items-center"
    style="height: 100%; visibility: hidden;">
    <i class="fas fa-sync fa-spin"></i>
    </div>`;
    document.querySelector('#customOut').innerHTML = loading_animation;
    document.querySelector('#customLoad').style.visibility = "visible";

    let script = editor.getValue();
    let lang = document.querySelector('#language').value;
    if (lang == 'none') {
        document.querySelector('#customOut').innerHTML = "Custom Output...";
        swal("Wait!", "Please select a language first.", "warning");
        return;
    }
    let callURL = `${document.location.protocol}//${document.location.host}/submitcode`;
    axios.post(callURL, {
        "lang": lang,
        "script": script,
        "lessonid": lessonId
    }).then(res => {
        document.querySelector('#customOut').innerHTML = "Custom Output...";
        if (res.data.verdict == 'pass') {
            let message = "You can move to next lesson now.";
            if (nextLesson == "None") message = "You can collect your certificate from home page.";
            swal("Good Job!", message, "success");
        }
        else swal("Uh Oh!", "Some testcases failed to pass. Try again.", "error");
    });
});

document.querySelector('#imgtotext').addEventListener('click', () => {
    let loading_animation = `<div id="customLoad" class="fa-4x d-flex justify-content-center align-items-center"
    style="height: 100%; visibility: hidden;">
    <i class="fas fa-sync fa-spin"></i>
    </div>`;
    document.querySelector('#customOut').innerHTML = loading_animation;
    document.querySelector('#customLoad').style.visibility = "visible";
    
    let imageURL = document.querySelector('#imageURL').value;
    let img = '<img src="' + imageURL + '">';
    let callURL = `${document.location.protocol}//${document.location.host}/imgtotext`;
    axios.post(callURL, {
        "imageURL": imageURL
    }).then(res => {
        document.querySelector('#customOut').innerHTML = "Custom Output...";
        if (res.data.status == 'fail') {
            swal("Uh Oh!", res.data.text, "error");
            return;
        }
        editor.getDoc().setValue(res.data.text);
        document.querySelector('#image').innerHTML = img;
    })
})