$(document).ready(function () {

	var qNumber=0;
	var qbank=new Array();
	var opArray=new Array();
	var myloader="activity.json";
	var stage="#game1";
	var stage2=new Object;
	var qlock=false;
	var numberOfQuestions;
	var score=0;

	fillDB();

	function fillDB(){



		$.getJSON(myloader, function(data) {

			//console.log(data);
			for(i=0;i<data.quizlist.length;i++){

				qbank[i]=new Array;
				qbank[i][0]=data.quizlist[i].question;
				qbank[i][1]=data.quizlist[i].option1;
				qbank[i][2]=data.quizlist[i].option2;
				qbank[i][3]=data.quizlist[i].option3;
				qbank[i][4]=data.quizlist[i].option4;
				qbank[i][5]=data.quizlist[i].voice;

			}
			numberOfQuestions=qbank.length;
			console.log(qbank);
			//alert(qbank);

			displayQuestion();


		})//gtjson

	}//filldb






	function generateRndSeq(n){

		var A = new Array;
		var rnd;
		for (var i = 0; i < n; i++){
			A[i] = i + 1;
		}
		for (var i = 0; i < n - 1; i++) {
			rnd = Math.random() * (n - i);
			rnd = Math.floor(rnd);
			temp = A[i];
			A[i] = A[rnd+i];
			A[rnd+i] = temp;
		}
		return A;
	}

	function displayQuestion(){

		var seq = generateRndSeq(4);
		//console.log(q);
		var ansid;
		var s = '<div class="questionText">' + qbank[qNumber][0] + '</div>';
		for (var i = 0; i < 4; i++) {
			if (seq[i] == 1) {ansid = i;}
			s = s + '<div id="' + i + '" class="pix"><img src=' + qbank[qNumber][seq[i]] + '"../resource/img"></div>';

		}

		var audio = new Audio("/voice/" + qbank[qNumber][5]);
		audio.play();

		//console.log(s);
		$(stage).append(s);
		$('.pix').click(function(){
			if(qlock==false){qlock=true;
				//correct answer
				if(this.id==ansid){
					$(stage).append('<div class="feedback1">CORRECT</div>');
					score++;
				}
				//wrong answer
				if(this.id!=ansid){
					$(stage).append('<div class="feedback2">WRONG</div>');


				}

				setTimeout(function(){changeQuestion()},1000);

			}})



	}//display question





	function changeQuestion(){

		qNumber++;

		if(stage=="#game1"){stage2="#game1";stage="#game2";}
		else{stage2="#game2";stage="#game1";}

		if(qNumber<numberOfQuestions){displayQuestion();}else{displayFinalSlide();}

		$(stage2).animate({"right": "+=800px"},"slow", function() {$(stage2).css('right','-800px');$(stage2).empty();});
		$(stage).animate({"right": "+=800px"},"slow", function() {qlock=false;});
	}//change question




	function displayFinalSlide(){

		$(stage).append('<div class="questionText">You have finished the quiz!<br><br>Total questions: '+numberOfQuestions+'<br>Correct answers: '+score+'</div>');

	}//display final slide





});//doc ready