// var hostAddr = '127.0.0.1:8000';
var hostAddr = 'esldownloader1.cloudapp.net';

var main = function()
{
    $('.btn').click(function() {

        document.treenumber=true;

        $('.tree').empty();
        jQuery.getScript("./parse_tree.js");
        $('.posts').empty();
        var post = $('.status-box').val();
        var post1 = post.split(" ");
        for(var i = 0; i < post1.length; i++)
        {
            var div = $('<div>');
            div.
            appendTo('.posts')
            .text(post1[i])
            .attr("width", function(){return (post1[i].length * 15).toString() + "px";});
            //display:inline-block
           // div.classed("active", "true");
            div.addClass("word");

            div.css({
           '-moz-user-select':'-moz-none',
           '-moz-user-select':'none',
           '-o-user-select':'none',
           '-khtml-user-select':'none', 
           '-webkit-user-select':'none',
           '-ms-user-select':'none',
           'user-select':'none'});
            
          //  console.log((post1[i].length * 15).toString() + "px");
            //
        }
   //     $('.status-box').val('');
    });

    $('.btn1').click(function(){
        var sentence = $('.status-box').val();
        var word_pos = "";
        var i = 0;
        $(".word").each(function(){
            if($(this).attr("class") == "word active")
                {  word_pos = word_pos + (i + " ");  }
            i++;
        })

    //    console.log(sentence);
    //    console.log(word_pos);
        $.getJSON("http://" + hostAddr + "/search2/", {"sentence":sentence, "word_pos":word_pos}, 
            function(data){
                console.log(data);
            //    r = $.map(data, function (item) { return item.sentence + '<br>' });
            //    $('.output').html(r);
            //        data = [{ list:"0 2 3",  sentence:"a b c d e"},  { list:"2 3",  sentence:"0 1 2 3 4 5 6 7 8 9 10"}];
            var answer = "", words = [], pos = [];
            for(var o in data)
            {
                words = data[o].sentence.split(' ');
                pos = data[o].list.split(' ');
                for(var i in pos)
                {
                    words[pos[i]] = "<span>" + words[pos[i]] + "</span>";
                }
                words = words.join(' ');
                answer += "<div class=\"sentence\">" + words + "</br>" + "</div>";
            }
     //       console.log(answer)
   //     r = $.map(data, function (item) { return item.sentence + '<br>' }); 
   
                $('.output').html(answer);
            });





       // $('.status-box').val('');
    })
    

    document.ismousedown = false;
    $('div').on('mousedown','.word', function(){
            document.ismousedown =true;
            if(!$(this).hasClass("active"))
                { $(this).addClass("active"); }
            else { $(this).removeClass("active"); }
          //  console.log($(this).hasClass("active"));

        });


    $('div').on('mouseover','.word', function(){ 
            if(document.ismousedown){
                if(!$(this).hasClass("active"))
                    { $(this).addClass("active"); }
                else  { $(this).removeClass("active"); }
            }
        });

    $('body').on('mouseup', function(){ 
       // console.log("aaa");
            document.ismousedown = false;
        });

    $(document).on("click",".sentence", function(text){
        console.log('clicked');
        document.treetext = $(this).text();
        jQuery.getScript("./parse_tree1.js");

    });


    }

  
$(document).ready(main);
