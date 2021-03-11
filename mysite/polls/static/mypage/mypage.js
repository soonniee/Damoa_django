document.querySelector('.custom-file-input').addEventListener('change',function(e){
    var fileName = document.getElementById("customFile").files[0].name;
    console.log(fileName)
    var nextSibling = e.target.nextElementSibling;
    nextSibling.innerText = fileName;
  })
  document.getElementById('possible').onclick = function() {
    
    if (document.getElementById('possible').checked) {
        document.getElementById('now_input').style.display = 'inline-block';
        document.getElementById('now_title').style.paddingTop = '10px';
    } else {
        document.getElementById('now_input').style.display = 'none';
    }
  };
  document.getElementById('impossible').onclick = function() {
    
    if (document.getElementById('impossible').checked) {
        document.getElementById('now_input').style.display = 'none';
    } else {
        document.getElementById('now_input').style.display = 'inline-block';
        document.getElementById('now_title').style.paddingTop = '10px';
    }
  };
  