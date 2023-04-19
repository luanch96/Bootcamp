function makeProgress(){
    if(percentage < 100){
      percentage = percentage + 1;
        bar.style.width = percentage + "%";
    }else if(percentage >= 100){
      fetchKey();
    }

    // Wait for sometime before running this script again
    setTimeout("makeProgress()", 300);
}
makeProgress();

function updateMasterKey(){
  fetch('/totp', {
      method: "POST",
      headers: {
          "Content-type": "application/json;charset=UTF-8"
      },
      body: JSON.stringify({'new_master_password': document.getElementById('master-password').value})
  })
  .then(function (response) {
      fetch_status = response.status;
      return response.json();
  }) 
  .then(function (json) {
      if (fetch_status == 200) {
          if(json.success){
            document.getElementById("toast-body-content").innerHTML = "<h4>Password updated successfully!</h4>";
            showToast();
          }else{
            html = "<h4>Password not updated!</h4>"
            html += "<p>" + json.error + "</p>";
            document.getElementById("toast-body-content").innerHTML = html;
            showToast();
          }
      }
  });
}

function fetchKey(){
  var fetch_status;
  masterPassword = document.getElementById('master-password').value;
  fetch('/totp/master_password=' + masterPassword, {
      method: "GET",
      headers: {
          "Content-type": "application/json;charset=UTF-8"
      }
  })
  .then(function (response) {
      fetch_status = response.status;
      return response.json();
  }) 
  .then(function (json) {
      if (fetch_status == 200) {
          document.getElementById("totp-key").innerHTML = json.key;
          document.querySelector(".progress-bar").style.width = json.percentage_to_next + "%";
          percentage = json.percentage_to_next;
          if(json.success){
            document.getElementById("happy-face").innerHTML = "😄";
            document.getElementById("toast-body-content").innerHTML = "<h4>🔓 Correct Password!</h4>";
            showToast();
          }else{
            document.getElementById("happy-face").innerHTML = "😞";
            document.getElementById("toast-body-content").innerHTML = "<h4>🔒 Incorrect Password!</h4";
            showToast();
          }
      }
  });
}

function generateMasterKey(){
    fetch('/new-master-key', {
        method: "GET",
        headers: {
            "Content-type": "application/json;charset=UTF-8"
        }
    })
    .then(function (response) {
        fetch_status = response.status;
        return response.json();
    }) 
    .then(function (json) {
        if (fetch_status == 200) {
            document.getElementById("new-master-key").value = json.new_master_key;
        }
    });
}

function showToast(){
  var toast = toastList[0];
  toast.show();
}

function loadToasts(){
  toastList = [].slice.call(document.querySelectorAll('.toast'))
  toastList = toastList.map(function (toastEl) {
      toast = new bootstrap.Toast(toastEl);
      return toast;
  })
}

window.addEventListener('load', function() {
  loadToasts();
});
