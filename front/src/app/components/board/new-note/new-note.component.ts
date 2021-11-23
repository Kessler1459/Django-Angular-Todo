import { Component, EventEmitter, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Category } from 'src/app/models/category';
import { Note } from 'src/app/models/note';

@Component({
    selector: 'app-new-note',
    templateUrl: './new-note.component.html',
    styleUrls: ['./new-note.component.scss']
})
export class NewNoteComponent implements OnInit {
    createEmitter = new EventEmitter<Note>();
    form=new FormGroup({
        name:new FormControl(""),
        category:new FormControl(1),
        description:new FormControl("")
    })
    
    constructor(@Inject(MAT_DIALOG_DATA) public categories:Category[]) { }

    ngOnInit(): void {
    }

    onSubmit(){
        if(this.form.valid){
            const newNote= new Note();
            newNote.name=this.form.value.name;
            newNote.category=this.form.value.category;
            newNote.description=this.form.value.description;
            this.createEmitter.emit(newNote);
        }
    }

}
