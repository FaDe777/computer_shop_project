
$('.yyy').each(function(ind,obj){
        $(obj).submit(function(elem){
            $.ajax({
                data: {
                    value : $(this).find('input[name="value"]').val(),
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                    dataType: "json"
                },
                type: "POST",
                url: "{% url 'cart_add' %}",
                success: function(response){
                    console.log($(this).serialize())
                    var new_obj = $('<a class="btn-cart btn-parent a-cart" href="{% url 'cart' %}"><span style="display: inline-block; margin: 16px 0;">В корзине</span></a>')
                    $(obj).replaceWith(new_obj)
                }
            });
            elem.preventDefault()
        });
    });

$('.likes').each(function(ind,obj){
    $(obj).submit(function(elem){
        $.ajax({
            data: {
                value: $(this).find('input[name="value"]').val(),
                csrfmiddlewaretoken: '{{ csrf_token }}',
                dataType: 'json',
                type: 'like',
            },
            type: "POST",
            url: "{% url 'comment_like' %}",
            success: function(response){

                if (response.act == 'True') {
                    console.log($('#add' + response.pk))
                    $('#l' + response.pk).find('button[name="add"]').replaceWith('<button class="svg-like" style="background-image: url({% static "components/images/like-active.svg" %})" type=submit id=remove' + response.pk + ' name=remove></button>')

                }
                else {
                    obj1 = '<button class="svg-like" style="background-image: url({% static "components/images/like.svg" %})" id="add' + response.pk + '" type="submit" name="add"></button>'
                    $('#remove' + response.pk).replaceWith(obj1)
                }

                $('#l' + response.pk).find('span[name="count"]').replaceWith('<span name="count" id="count{{i.pk}}">' + response.likes + '</span>')

                if (response.re_dis == 'True'){
                    $('#d' + response.pk).find('span[name="count"]').html(response.dislikes)
                    $('#d' + response.pk).find('button[name="remove"]').replaceWith('<button class="svg-like" style="background-image: url({% static "components/images/dislike.svg" %})" type="submit" name="add"></button>')
                }
            }

        });

        elem.preventDefault()
    });
});

$('.dislikes').each(function(ind,obj){
    $(obj).submit(function(elem){
        $.ajax({
            data: {
                value: $(this).find('input[name="value"]').val(),
                dataType: 'json',
                csrfmiddlewaretoken: '{{csrf_token}}',
                type: 'dislike',
            },
            type: "POST",
            url: "{% url 'comment_like' %}",
            success: function(response){

                if (response.act == 'True'){
                    $(obj).find('button[name="add"]').replaceWith('<button class="svg-like" style="background-image: url({% static "components/images/dislike-active.svg" %})" type="submit" name="remove"></button>')
                }
                else {
                    $(obj).find('button[name="remove"]').replaceWith('<button class="svg-like" style="background-image: url({% static "components/images/dislike.svg"" %})" type="submit" name="add"></button>')
                }
                $(obj).find('span[name="count"]').html(response.dislikes)

                if (response.re_like == 'True'){
                    $('#l' + response.pk).find('span[name="count"]').html(response.likes)
                    console.log($('#add' + response.pk))
                    $('#l' + response.pk).find('button[name="remove"]').replaceWith('<button class="svg-like" style="background-image: url({% static "components/images/like.svg" %})" type="submit" name="add"></button>')
                }
            }
        });
        elem.preventDefault()
    });
});

