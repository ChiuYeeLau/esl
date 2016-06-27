// var hostAddr = '127.0.0.1:8000';
var hostAddr = 'esldownloader1.cloudapp.net:8000';

var main = function()
{
    $('.btn-post').click(function() {

        document.treenumber=true;

        $('.tree').empty();
        // jQuery.getScript("./parse_tree.js");
        parse_tree();
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

    $('.btn-submit').click(function(){
        var $btn = $(this).button('loading');
        var sentence = $('.status-box').val();
        var word_pos = "";
        var i = 0;
        $(".word").each(function(){
            if($(this).attr("class") == "word active")
                {  word_pos = word_pos + (i + " ");  }
            i++;
        })
        if (!word_pos) {
            alert('No keywords selected');
            return;
        }

    //    console.log(sentence);
    //    console.log(word_pos);
        $.getJSON("http://" + hostAddr + "/search2/", {"sentence":sentence, "word_pos":word_pos}, 
            function(data){
                // console.log(data);
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
                    answer += "<li class=\"sentence\">" + words + "</li>";
                }
            //     console.log(answer)
            //     r = $.map(data, function (item) { return item.sentence + '<br>' }); 
   
                $('.output').html(answer);
                $btn.button('reset');
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
        // console.log('clicked');
        document.treetext = $(this).text();
        // jQuery.getScript("./parse_tree1.js");
        parse_tree1();
    });
}

  
$(document).ready(main);


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



    var flare = $.get("http://" + hostAddr + "/syntaxtree/", {"tree":post}, 
            function(data){
                
      data = d3.csvParse(data);
                      

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



    var flare = $.get("http://" + hostAddr + "/syntaxtree/", {"tree":post}, 
            function(data){
               // console.log(data); 
      data = d3.csvParse(data);
                      

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
