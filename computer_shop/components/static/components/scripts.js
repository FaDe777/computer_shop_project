function show_hide_password(elem) {
    var input = document.getElementById('id_password');
    if (input.getAttribute('type') == 'password'){
        elem.classList.add('view')
        input.setAttribute('type','text')
    }
    else {
        elem.classList.remove('view')
        input.setAttribute('type','password')
    }
    return false;
}

function showReviewForm() {
    var form = document.getElementById('review-form')
    var btn = document.getElementById('review-btn')

    if (form.classList.contains('open')) {
        form.classList.remove('open')
        btn.innerHTML = "Добавить отзыв"
    }
    else {
        form.classList.add('open')
        btn.innerHTML = "Скрыть форму"
    }
}

function showComments(elem){
    var form = $('#f_w_c' + elem)

    if (form[0].style.display == '' || form[0].style.display == 'none'){
        form[0].style.display = 'block';
    }
    else {
        form[0].style.display = 'none';
    }
}

function showReplyForm(elem){
    var form = $('#r_f_w' + elem)

    if (form[0].style.display == '' || form[0].style.display == 'none'){
        form[0].style.display = 'block';
        var text = form.find('textarea[name="text"]')[0]
        var name = $('#author' + elem)[0].innerHTML
        text.value = '@' + name + ', '
    }
    else {
        form[0].style.display = 'none';
    }
}

function confirmDelete(elem){
    var dark = $('#popup' + elem)[0]
    dark.style.display = 'block';
    $('body').css('overflow','hidden');
    toggleBodyScroll(true);
}

function closeConfirm(elem){
    var dark = $('#popup' + elem)[0]
    dark.style.display = 'none';
    $('body').css('overflow','visible');
    toggleBodyScroll(false);
}

$("#add").submit(function(e) {
    var data = $("#add").serialize()
    $.ajax({
        data: data,
        type: "POST",
        url: "{% url 'cart_add_ajax' %}",
        success: function(total){
            $('#huy').html(total.total)
            }
    });
    e.preventDefault()
});

$('#add').submit(function(e) {
    var data = $("#add").serialize()
    $.ajax({
        data: data,
        type: "POST",
        url: "{% url 'cart_add_ajax' %}",
    });
    e.preventDefault()
})


let offset = 0;
const sliderLine = document.querySelector('.slides');
let max = (document.querySelectorAll('.slide').length - 1) * -100;
sliderLine.style.width = (document.querySelectorAll('.slide').length * 100) + '%';


document.querySelector('.slider-left').addEventListener('click',function(){
    if (offset < 0){
        offset += 100;
    }
    sliderLine.style.left = offset + '%';
});

document.querySelector('.slider-right').addEventListener('click',function(){
    console.log(offset)
    if (offset > max){
         offset -= 100;
    }
    sliderLine.style.left = offset  + '%';
});

elems = document.querySelectorAll('.bar');

for (let i = 0; i < elems.length; i++) {
    elems[i].addEventListener('click',function(){
        offset = i * -100;
        sliderLine.style.left = offset + '%';
    });
}

function orderByRate(){
    var elems = $('.review')
    console.log(elems)
    elems.sort(function(a,b){
        return Number($('#rate' + b.id)[0].innerHTML) - Number($('#rate' + a.id)[0].innerHTML)
    })
    console.log(elems)
    var ul = document.createElement('ul');
    ul.classList.add('reviews')

    for (var i = 0; i < elems.length; i++) {
        ul.appendChild(elems[i])
    }
    $('.reviews').replaceWith(ul)

}

function orderByTop(){
    var elems = $('.review')

    elems.sort(function(a,b){
        var a_sum = Number($('#lcount' + a.id)[0].innerHTML) - Number($('#dcount' + a.id)[0].innerHTML)
        var b_sum = Number($('#lcount' + b.id)[0].innerHTML) - Number($('#dcount' + b.id)[0].innerHTML)
        return b_sum - a_sum
    })

    var ul = document.createElement('ul');

    ul.classList.add('reviews')
    for (var i = 0; i < elems.length; i++) {
        ul.appendChild(elems[i])
    }
    $('.reviews').replaceWith(ul)
}

function orderByDate(){
    var elems = $('.review')

    elems.sort(function(a,b){
        var arr1 = $('#date' + a.id)[0].innerHTML.split('.').map(elem => Number(elem))
        var date1 = new Date(arr1[2],arr1[1],arr1[0])

        var arr2 = $('#date' + b.id)[0].innerHTML.split('.').map(elem => Number(elem))
        var date2 = new Date(arr2[2],arr2[1],arr2[0])

        return date2 - date1
    });

    var ul = document.createElement('ul');
    console.log(ul)
    ul.classList.add("reviews");
    for (var i = 0; i < elems.length; i++) {
        ul.appendChild(elems[i])
    }

    $('.reviews').replaceWith(ul)
}

$('.reply-form-wrap').each(function(ind,obj){
    $(obj).submit(function(elem){
        var form = elem.target
        $.ajax({
            data: {
                text: form.elements['text'].value,
                val: $(this).find('input[name="reply"]').val(),
                csrfmiddlewaretoken: $(this).find('input[name="csrfmiddlewaretoken"]').val(),
                dataType: "json"
            },
            type: "POST",
            url: $(this).attr('data-url'),
            success: function(response){
                var img = $('<img>')[0]

                if (response.img == 'True') {
                    img.src = response.src
                }
                else {
                    img.src = "/static/components/images/no-avatar.png"
                }

                img.classList.add("review-avatar")

                var elem = $('<div class="reply">' + '<div>' + img.outerHTML  + '</div>' + '</div>')

                $('#reply-wrap'+response.id).append(elem);
            }
        });
        elem.preventDefault()
    });
});

$('.reply-del').each(function(ind,obj){
    $(obj).submit(function(elem){

        $.ajax({
            data: {
                val: $(this).find('input[name="reply_delete"]').val(),
                csrfmiddlewaretoken: $(this).find('input[name="csrfmiddlewaretoken"]').val(),
                dataType: "json"
            },
            type: "POST",
            url: $(this).attr('data-url'),
            success: function(response){
                $('#reply' + response.pk).remove();
                console.log($('#comment-btn'+ response.r_id)[0])
                $('#comment-btn'+ response.r_id)[0].innerHTML = "Комментарии (" + response.count + ")"
            }
        });
        elem.preventDefault();
    });
});

