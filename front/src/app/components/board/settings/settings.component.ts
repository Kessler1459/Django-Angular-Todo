import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';
import { Category } from 'src/app/models/category';
import { User } from 'src/app/models/user';
import { AuthService } from 'src/app/services/auth.service';
import { BoardService } from 'src/app/services/board.service';
import { emailNotExistsAsyncValidator } from 'src/app/validators/email.async.validator';

@Component({
    selector: 'app-settings',
    templateUrl: './settings.component.html',
    styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
    categoriesForm: FormGroup;
    categories: Category[];
    guestsForm: FormGroup;
    guests: User[];
    boardId:number;

    constructor(private actRoute: ActivatedRoute,private location: Location, private boardService: BoardService, private authService: AuthService) { }

    ngOnInit(): void {
        this.boardId = Number(this.actRoute.snapshot.paramMap.get("boardId"));
        if (this.boardId) {
            this.boardService.getCategoriesOfBoard(this.boardId).subscribe(categories => this.categories = categories);
            this.boardService.getGuestsOfBoard(this.boardId).subscribe(guests => this.guests = guests);
        }
        this.categoriesForm=new FormGroup({
            name:new FormControl("",[Validators.required])
        })
        this.guestsForm = new FormGroup({
            email: new FormControl("", [Validators.required,Validators.email], [emailNotExistsAsyncValidator(this.authService)])
        })
    }

    onSubmitGuest(){
        if(this.guestsForm.valid){
            this.boardService.addGuestToBoard(this.boardId, this.guestsForm.value.email).subscribe(addedUser=>{
                this.guests.push(addedUser);
                this.guestsForm.controls.email.setValue("");
            })
        }
    }

    onSubmitCategory(){
        if(this.categoriesForm.valid){
            const newCat=new Category();
            newCat.name=this.categoriesForm.value.name;
            this.boardService.addCategoryToBoard(this.boardId, newCat).subscribe(addedCat=>{
                this.categories.push(addedCat);
                this.categoriesForm.controls.name.setValue("");
            })
        }
    }

    back(){
        this.location.back();
    }

}
