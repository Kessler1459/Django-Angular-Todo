import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map } from 'rxjs/operators';
import { Board } from '../models/board';
import { Column } from '../models/column';
import { Note } from '../models/note';

@Injectable({
    providedIn: 'root'
})
export class BoardService {
    private rootUrl = "http://localhost:8000/api/";

    constructor(private httpClient: HttpClient) { }

    addBoard(board:Board){
        return this.httpClient.post<Board>(this.rootUrl+'boards', board);
    }

    getOwnedBoards(userId: number){
        return this.httpClient.get<Board[]>(this.rootUrl + 'user/'+userId+'/boards').pipe(
            map(list=>list??[])
        );
    }

    getGuestedBoards(guestId: number) {
        return this.httpClient.get<Board[]>(this.rootUrl + 'boards/guests/' + guestId).pipe(
            map(list=>list??[])
        );
    }

    getBoard(boardId: number) {
        return this.httpClient.get<Board>(this.rootUrl + 'boards/' + boardId);
    }

    deleteBoard(boardId: number){
        return this.httpClient.delete<any>(this.rootUrl + 'boards/' + boardId);
    }

    addColumn(newCol: Column, boardId: number) {
        return this.httpClient.post<Column>(`${this.rootUrl}boards/${boardId}/columns`, newCol);
    }

    deleteColumn(columnId: number) {
        return this.httpClient.delete(this.rootUrl + 'columns/' + columnId);
    }

    addNote(note: Note, columnId: number) {
        return this.httpClient.post<Note>(`${this.rootUrl}columns/${columnId}/notes`, note)
    }

    changeNoteColumn(noteId: number, newColumnId: number) {
        return this.httpClient.put(this.rootUrl + "notes/" + noteId + "/column", { column: newColumnId });
    }

    editNote(editNote: Note) {
        return this.httpClient.put(this.rootUrl + 'notes/' + editNote.id, editNote);
    }

    deleteNote(noteId: number) {
        return this.httpClient.delete(this.rootUrl + 'notes/' + noteId);
    }
}
