import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Column } from 'src/app/models/column';

@Component({
    selector: 'app-add-column',
    templateUrl: './add-column.component.html',
    styleUrls: ['./add-column.component.scss']
})
export class AddColumnComponent implements OnInit {
    form:FormGroup= new FormGroup({
        name: new FormControl("", [Validators.required])
    })
    
    @Output()
    addColumn=new EventEmitter<Column>();

    constructor() { }

    ngOnInit(): void {
    }

    onSubmit(){
        if(this.form.valid){
            const col=new Column();
            col.name=this.form.value.name;
            this.addColumn.emit(col);
        }
    }
}
