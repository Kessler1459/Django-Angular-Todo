import { Component, EventEmitter, Inject, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Category } from 'src/app/models/category';
import { Note, State } from 'src/app/models/note';

@Component({
    selector: 'app-note',
    templateUrl: './note.component.html',
    styleUrls: ['./note.component.scss']
})
export class NoteComponent implements OnInit {
    @Output()
    deleteNoteEmitter = new EventEmitter<Note>();
    @Output()
    editNoteEmitter = new EventEmitter<Note>();
    editing = false;
    form = new FormGroup({
        name: new FormControl(this.data.note.name, [Validators.required]),
        description: new FormControl(this.data.note.description),
        category: new FormControl(this.data.note.category.id, [Validators.required])
    })
    constructor(@Inject(MAT_DIALOG_DATA) public data: { note: Note, categories: Category[] }) { }

    ngOnInit(): void {
    }

    deleteNote() {
        this.deleteNoteEmitter.emit(this.data.note);
    }

    onSubmit() {
        if (this.form.valid) {
            const values = this.form.value;
            this.data.note.name = values.name;
            this.data.note.description = values.description;
            this.data.note.category = this.data.categories.find(cat => cat.id == values.category) ?? this.data.note.category;
            this.editNoteEmitter.emit(this.data.note)
        }       
    }

    toggleEdit() {
        this.editing = !this.editing;
    }

    dateFormat(date: Date) {
        return new Date(date)
    }

    enumAsString(state: State) {
        return (Object.values(State)[Object.keys(State).indexOf(state)]);
    }
}
