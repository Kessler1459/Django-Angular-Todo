import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth.service';


@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
    form: FormGroup;
    este: boolean;
    constructor(private authService: AuthService,private router:Router) { }

    ngOnInit(): void {
        this.form = new FormGroup({
            email: new FormControl("", [Validators.email, Validators.required]),
            password: new FormControl("", [Validators.required, Validators.minLength(7)])
        })

    }

    onSubmit() {
        if (this.form.valid) {
            this.authService.login(this.form.value.email, this.form.value.password).subscribe(
                () => this.router.navigateByUrl(""), 
                error => console.log(error)
            )

        }
    }

    whatuser() {
        //return this.authService.token
       // return this.authService.isloggedIn().subscribe(is => this.este = is)
    }

}
