$(document).ready(function(){

    $('.bookmarkButton').on('click', function(){
        let book_id = $(this).attr('word_id');
        req = $.ajax({
            url: '/update',
            type: 'POST',
            data: {id: book_id}
        });

        req.done(function(data) {
            let cur_state = $('.bookmarkButton#bookmark_'+book_id).attr('class');
            if(cur_state.indexOf("btn-outline-success") != -1){  //if bookmarked
                cur_state = cur_state.replace("btn-outline-success","btn-outline-secondary");
            } else { //if not bookmark
                cur_state = cur_state.replace("btn-outline-secondary","btn-outline-success");
            }
            $('.bookmarkButton#bookmark_'+book_id).attr('class',cur_state);
        });
    });

    $('.audioButton').on('click', function(){
        let audio_id = $(this).attr('audio_id');
        let audioElement = $('#'+audio_id);
        audioElement[0].play();
    });

});