import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Board } from 'src/app/models/board';
import { AuthService } from 'src/app/services/auth.service';
import { BoardService } from 'src/app/services/board.service';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
    guestBoards:Board[];
    yourBoards:Board[];
    form=new FormGroup({
        name:new FormControl("",[Validators.required])
    })
    constructor(private authService: AuthService, private boardService: BoardService,private router:Router) { }

    ngOnInit(): void {
        if(this.authService.user){
            this.boardService.getOwnedBoards(this.authService.user.id).subscribe(boards=>this.yourBoards=boards)
            this.boardService.getGuestedBoards(this.authService.user.id).subscribe(boards=>this.guestBoards=boards)
        }           
    }

    onSubmitBoard(){
        if(this.form.valid){
            const newBoard=new Board();
            newBoard.name=this.form.value.name;
            this.boardService.addBoard(newBoard).subscribe(createdBoard=>{
                this.yourBoards.push(createdBoard);
                this.form.controls.name.setValue("");
            });
        }
    }

    toBoard(boardId:number){
        this.router.navigateByUrl("/boards/"+boardId);
    }
}
