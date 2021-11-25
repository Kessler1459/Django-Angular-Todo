import { NgModule } from '@angular/core';
import { CookieModule } from 'ngx-cookie';
import { BrowserModule } from '@angular/platform-browser';
import { ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavComponent } from './components/nav/nav.component';
import { SignupComponent } from './components/signup/signup.component';
import { LoginComponent } from './components/login/login.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatFormFieldModule } from '@angular/material/form-field'
import { MatInputModule } from '@angular/material/input'
import { DragDropModule } from '@angular/cdk/drag-drop'
import { MatButtonModule } from '@angular/material/button'
import { AuthInterceptorService } from './services/auth-interceptor.service';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { BoardComponent } from './components/board/board.component';
import { AddColumnComponent } from './components/board/add-column/add-column.component';
import { MatDialogModule } from "@angular/material/dialog";
import { MatIconModule } from '@angular/material/icon';
import { NoteComponent } from './components/board/note/note.component';
import { NewNoteComponent } from './components/board/new-note/new-note.component';
import {MatSelectModule} from '@angular/material/select';
import { SettingsComponent } from './components/board/settings/settings.component'

@NgModule({
    declarations: [
        AppComponent,
        NavComponent,
        SignupComponent,
        LoginComponent,
        DashboardComponent,
        BoardComponent,
        AddColumnComponent,
        NoteComponent,
        NewNoteComponent,
        SettingsComponent

    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        BrowserAnimationsModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        HttpClientModule,
        CookieModule.forRoot(),
        MatDialogModule,
        MatIconModule,
        MatSelectModule,
        DragDropModule
    ],
    providers: [{
        provide: HTTP_INTERCEPTORS,
        useClass: AuthInterceptorService,
        multi: true
    }],
    bootstrap: [AppComponent]
})
export class AppModule { }
