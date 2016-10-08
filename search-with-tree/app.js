var hostAddr = '127.0.0.1:8000';
// var hostAddr = 'www.eslwriter.org:8005';

$(document).ready(function() {
    $('.btn-reset').click(function() {
        $('div.word').removeClass('active');
    });

    $('.btn-post').click(function() {
        document.treenumber=true;
        $('.tree').empty();
        parse_tree();
    });

    $('.btn-submit').click(function(){
        var sentence = $('.status-box').val();
        var word_pos = "";
        var i = 0;
        $(".word").each(function(){
            word_pos = word_pos + (i + " ");
            i++;
        });
        if (!word_pos) {
            alert('No keywords selected');
            return;
        }
        var $btn = $(this).button('loading');
        function jsonBack(data){
            var numResults = 0;
            $('.output').empty();
            for (i=0; i < data.desc.sen.length; i++)
                numResults += data.desc.sen[i].count;
            $(data.desc.sen).each(function(_, g) {
                var li = $('<li>').html(g.display + ' (' + g.count + ')').
                    append($('<ul class="sentence-group">').attr('data-id', g.id)).appendTo('.output');
                li.find('a').click(function(){
                    // console.log($(this).attr('pos'));
                    var new_pos = "";
                    var i = 0;
                    for (i=0; i < g.pos.length; i++) {
                        new_pos += g.pos[i] + " ";
                    }
                    $.getJSON("http://" + hostAddr + '/search8/',
                              {"sentence":g.title, "word_pos":new_pos, "next_pos":$(this).attr('pos')}, jsonBack);
                });
            });
            $(data.result).each(function(_, r) {
                /*
                var words = r.sentence.split(' '),
                    pos = r.list.split(' ');
                $(pos).each(function(_, p) {
                    words[Number(p)] = '<span>' + words[Number(p)] + '</span>';
                });
                $('<li class="sentence">').html(words.join(' ')).appendTo('ul.sentence-group[data-id="' + r.sen + '"]');
                */
                $('<li class="sentence">').html(r.sentence).appendTo('ul.sentence-group[data-id="' + r.sen + '"]');
            });
            $('.num-results').text(numResults);
            $btn.button('reset');
        }

        $.getJSON("http://" + hostAddr + $(this).attr('data-url'), {"sentence":sentence, "word_pos":word_pos}, jsonBack);
       // $('.status-box').val('');
    });

    var ajaxTimer;
    function onInputChange() {
        // delayed call
        if (ajaxTimer) {
            clearTimeout(ajaxTimer);
        }
        ajaxTimer = setTimeout(function() {
            console.log($('.status-box').val());
            $('.btn-post').click();
        }, 500);
    }
    onInputChange();

    var area = $('.status-box')[0]
    if (area.addEventListener) {
        area.addEventListener('input', onInputChange, false);
    } else if (area.attachEvent) {
        area.attachEvent('onpropertychange', onInputChange);
    }

    function generateTokens(tokens) {
        $('.posts').empty();
        var post1 = tokens;
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
    }


    function parse_tree() {
        var originconsole = console;
        //var drag = d3.behavior.drag()
        //          .on('dragstart', dragstart)
        //          .on('drag', dragmove)
        //          .on('dragend', dragend);
        var width = 600,
            height = 600;

        var zoomListener = d3.behavior.zoom().scaleExtent([0.1, 3]).on("zoom", function () {
          svg1.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
        });

        var cluster = d3.cluster().size([height, width - 160]);


        var stratify = d3.stratify()
            .parentId(function(d) { return d.id.substring(0, d.id.lastIndexOf("@")); });

        var svg1_tmp = d3.select(".tree").append("svg")
            .attr("width", width)
            .attr("height", "50%");

            svg1_tmp.call(zoomListener);
        if(document.treenumber==true)
        {
          var svg1 = svg1_tmp
            .attr("class", "tree1")
            .append("g")
            .attr("transform", "translate(40,0)")
            ;
            var post = $('.status-box').val();
          }
          else
        {
          d3.select("#tree2").remove();
          var svg1 = svg1_tmp
            .attr("id", "tree2")
            .append("g")
            .attr("transform", "translate(40,0)")
            ;
            var post = document.treetext;
          }



        var flare = $.get("http://" + hostAddr + "/syntaxtree/", {"tree":post}, function(data){
            // TODO: initialize blocks

            generateTokens($(data.tokens).map(function(_, token) { return token.t; }));
            data = d3.csvParse(data.tree);


        //d3.csv("flare.csv", function(error, data) {
        //  if (error) throw error;

          var root = stratify(data);


        //      .sort(function(a, b) { return (a.height - b.height) || a.id.localeCompare(b.id); });
         // console.log(root);
          cluster(root);

          var link = svg1.selectAll(".link")
              .data(root.descendants().slice(1))
            .enter().append("path")
              .attr("class", "link")
              .attr("d", function(d) {
                return "M" + d.y + " "
                + d.x + "L" + d.parent.y + " "
                + d.parent.x;
              });
          //console.log(link);

          var node = svg1.selectAll(".node")
              .data(root.descendants())
              .enter().append("g")
              .attr("class", function(d) { return "node" + (d.children ? " node--internal" : " node--leaf"); })
              .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

         // node.append("circle")
         //     .attr("r", 2.5);
         // console.log(root.descendants());
         /* var rect = node
                  .append("rect")
              //  .attr("class", "node")
                .attr("width", 20)
            .attr("height", 10)
          //      .attr("x", function(d){  return d.y;})
          //      .attr("y", function(d){  return d.x;});
         //             .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
             .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });*/
         // console.log(svg1.selectAll(".node--leaf"));
          node.append("text")
              .attr("dy", 3)
              .attr("x", function(d) { return d.children ? -8 : 8; })
         //     .style("text-anchor", function(d) { return d.children ? "end" : "start"; })
              .style("margin", "10px")
              .text(function(d) {
             //   console.log(d.id.lastIndexOf("@"));
             //   console.log(d.id.substring(d.id.lastIndexOf("@") + 1));
                return d.id.substring(d.id.lastIndexOf("@") + 1); });
              document.treenumber = false;
        });
    }

    function parse_tree1() {
        var originconsole = console;
        function zoom() {
                svg2.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
            }
        //var drag = d3.behavior.drag()
        //          .on('dragstart', dragstart)
        //          .on('drag', dragmove)
        //          .on('dragend', dragend);
        var width = 600,
            height = 600;

        var zoomListener = d3.behavior.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);

        var cluster = d3.cluster()
            .size([height, width - 160])
            ;


        var stratify = d3.stratify()
            .parentId(function(d) { return d.id.substring(0, d.id.lastIndexOf("@")); });

        var svg2_tmp = d3.select(".tree").append("svg")
            .attr("width", width)
            .attr("height", "50%");

            svg2_tmp.call(zoomListener);
        if(document.treenumber==true)
        {
          var svg2 = svg2_tmp
            .attr("class", "tree1")
            .append("g")
            .attr("transform", "translate(40,0)")
            ;
            var post = $('.status-box').val();
          }
          else
        {
          d3.select("#tree2").remove();
          var svg2 = svg2_tmp
            .attr("id", "tree2")
            .append("g")
            .attr("transform", "translate(40,0)")
            ;
            var post = document.treetext;
          }



        var flare = $.get("http://" + hostAddr + "/syntaxtree/", {"tree":post}, function(data){
            // console.log(data);
            data = d3.csvParse(data.tree);


        //d3.csv("flare.csv", function(error, data) {
        //  if (error) throw error;

          var root = stratify(data);


        //      .sort(function(a, b) { return (a.height - b.height) || a.id.localeCompare(b.id); });
         // console.log(root);
          cluster(root);

          var link = svg2.selectAll(".link")
              .data(root.descendants().slice(1))
            .enter().append("path")
              .attr("class", "link")
              .attr("d", function(d) {
                return "M" + d.y + " "
                + d.x + "L" + d.parent.y + " "
                + d.parent.x;
              });
          //console.log(link);

          var node = svg2.selectAll(".node")
              .data(root.descendants())
              .enter().append("g")
              .attr("class", function(d) { return "node" + (d.children ? " node--internal" : " node--leaf"); })
              .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });

         // node.append("circle")
         //     .attr("r", 2.5);
         // console.log(root.descendants());
         /* var rect = node
                  .append("rect")
              //  .attr("class", "node")
                .attr("width", 20)
            .attr("height", 10)
          //      .attr("x", function(d){  return d.y;})
          //      .attr("y", function(d){  return d.x;});
         //             .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
             .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });*/
         // console.log(svg2.selectAll(".node--leaf"));
          node.append("text")
              .attr("dy", 3)
              .attr("x", function(d) { return d.children ? -8 : 8; })
         //     .style("text-anchor", function(d) { return d.children ? "end" : "start"; })
              .style("margin", "10px")
              .text(function(d) {
             //   console.log(d.id.lastIndexOf("@"));
             //   console.log(d.id.substring(d.id.lastIndexOf("@") + 1));
                return d.id.substring(d.id.lastIndexOf("@") + 1); });
              document.treenumber = false;
        });
    }


    document.ismousedown = false;
    $('div').on('mousedown','.word', function(){
        document.ismousedown =true;
        if(!$(this).hasClass("active"))
            { $(this).addClass("active"); }
        else { $(this).removeClass("active"); }
        // console.log($(this).hasClass("active"));
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
        // console.log('clicked');
        document.treetext = $(this).text();
        // jQuery.getScript("./parse_tree1.js");
        parse_tree1();
    });
});
