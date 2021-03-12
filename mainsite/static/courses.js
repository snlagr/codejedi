let buts = document.querySelectorAll('.claimcert');

for (let i = 0; i < buts.length; i++) {
    buts[i].addEventListener('click', function () {
        let callURL = `${document.location.protocol}//${document.location.host}/claimcert`;
        axios.post(callURL, {
            "courseid": this.dataset.courseid
        }).then(res => {
            if (res.data.verdict == 'pass') {
                swal("Email Sent!", "Please check your inbox shortly.", "success");
            }
        });
    })
}