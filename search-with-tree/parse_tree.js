// var hostAddr = '127.0.0.1:8000';
var hostAddr = 'esldownloader1.cloudapp.net:8000';

var originconsole = console;
function zoom() {
        svg1.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
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
