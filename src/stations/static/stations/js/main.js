let lift_btns = document.querySelectorAll('.lift_btn')

if(lift_btns[0].classList.contains('custom_disabled')){
    lift_btns.forEach(btn => {
        btn.addEventListener('click', function(e){
            e.preventDefault()
        })
    })
}