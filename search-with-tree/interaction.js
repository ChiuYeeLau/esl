var main = function()
{
    
	document.ismousedown = false;

    $('g').on('mousedown','.node--leaf', function(){
            document.ismousedown =true;
            console.log($(this).attr("class") == "active");
            if(!($(this).attr("class") == "node node--leaf active"))
                { $(this).attr("class", "node node--leaf active"); }
            else 
                { $(this).attr("class", "node node--leaf"); }            
        });


    $('g').on('mouseover','.node--leaf', function(){ 
            if(document.ismousedown){
            if(!($(this).attr("class") == "node node--leaf active"))
                    { $(this).attr("class", "node node--leaf active");}
                else  
                    { $(this).attr("class", "node node--leaf"); }
            }
        });

    $('svg').on('mouseup', function(){ 
            document.ismousedown = false;
        });

    $('svg').on('mouseleave', function(){ 
            document.ismousedown = false;
        });

}

$(document).ready(main);