import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { Board } from 'src/app/models/board';
import { BoardService } from 'src/app/services/board.service';
import { AuthService } from 'src/app/services/auth.service';
import { AddColumnComponent } from './add-column/add-column.component';
import { Column } from 'src/app/models/column';
import { NoteComponent } from './note/note.component';
import { Note, State } from 'src/app/models/note';
import { NewNoteComponent } from './new-note/new-note.component';

@Component({
    selector: 'app-board',
    templateUrl: './board.component.html',
    styleUrls: ['./board.component.scss']
})
export class BoardComponent implements OnInit {
    board: Board;
    constructor(public authService: AuthService, private actRoute: ActivatedRoute, private boardService: BoardService, private matDialog: MatDialog, private router:Router) { }

    ngOnInit(): void {
        const id = this.actRoute.snapshot.paramMap.get("boardId");
        if (id) {
            this.boardService.getBoard(Number(id)).subscribe(board => this.board = board)
        }
    }

    openNewColumnDialog() {
        const dialogConfig = new MatDialogConfig();
        dialogConfig.hasBackdrop = true;
        const instance = this.matDialog.open(AddColumnComponent, dialogConfig);
        const subscribe = instance.componentInstance.addColumn.subscribe(newCol => { //subscribo al emitter dentro del dialog
            this.addColumn(newCol);
            instance.close();
        });
        instance.afterClosed().subscribe(() => subscribe.unsubscribe());                    //desubscribo cuando el dialog cierra
    }

    openNoteDialog(note: Note) {
        const dialogConfig = new MatDialogConfig();
        dialogConfig.hasBackdrop = true;
        dialogConfig.data = { note, categories: this.board.categories };
        const instance = this.matDialog.open(NoteComponent, dialogConfig);
        const subscribeDelete = instance.componentInstance.deleteNoteEmitter.subscribe(delNote => {
            this.onDeleteNote(delNote);
            instance.close();
        });
        const subscribeEdit = instance.componentInstance.editNoteEmitter.subscribe(editedNote => {
            this.onEditNote(editedNote);
            console.log("a");
            
            instance.close();
        })
        instance.afterClosed().subscribe(() => {
            subscribeDelete.unsubscribe();
            subscribeEdit.unsubscribe();
        });
    }

    openNoteFormDialog(columnId: number) {
        const dialogConfig = new MatDialogConfig();
        dialogConfig.hasBackdrop = true;
        dialogConfig.data = this.board.categories;
        const instance = this.matDialog.open(NewNoteComponent, dialogConfig);
        const subscribe = instance.componentInstance.createEmitter.subscribe(newNote => {
            this.onCreateNote(newNote, columnId);
            instance.close();
        });
        instance.afterClosed().subscribe(() => subscribe.unsubscribe());
    }

    addColumn(newColumn: Column) {
        this.boardService.addColumn(newColumn, this.board.id).subscribe(newCol => this.board.columns.push(newCol));
    }

    onDeleteColumn(column: Column) {
        this.boardService.deleteColumn(column.id).subscribe(() => this.board.columns.splice(this.board.categories.indexOf(column), 1));
    }

    onCreateNote(note: Note, columnId: number) {
        this.boardService.addNote(note, columnId).subscribe(newNote => this.board.columns.find(col => col.id == columnId)?.notes.push(newNote))
    }

    onDeleteNote(note: Note) {
        this.boardService.deleteNote(note.id).subscribe(() => {
            for (let column of this.board.columns) {
                const index = column.notes.indexOf(note);
                if (index) {
                    column.notes.splice(index, 1);
                    break;
                }
            }
        })
    }

    onEditNote(editedNote: Note) {
        this.boardService.editNote(editedNote).subscribe(edited=>{
            for (let column of this.board.columns) {
                const index = column.notes.findIndex(note=>note.id=editedNote.id)
                if (index) {
                    column.notes[index]=editedNote;
                    break;
                }
            }
        })
    }

    enumAsString(state: State) {
        return (Object.values(State)[Object.keys(State).indexOf(state)]);
    }

    onDeleteBoard(){
        this.boardService.deleteBoard(this.board.id).subscribe(()=> this.router.navigateByUrl(""))
    }

}