//
//  AppDelegate.swift
//  LLDO
//
//  Created by Sebastian Ludwig on 24.02.19.
//  Copyright (c) 2019 Julian Raschke und Sebastian Ludwig GbR. All rights reserved.
//

import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
    var window: UIWindow?
    
    func applicationDidBecomeActive(_ application: UIApplication) {
        print("➡️ break here")
    }
}

class ViewController: UIViewController {
    @IBOutlet private var usernameTextField: UITextField!
    @IBOutlet private var passwordTextField: UITextField!
    
    private func showMessase(_ message: String) {
        let alert = UIAlertController(title: message, message: nil, preferredStyle: .actionSheet)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
        print(message)
    }
    
    @IBAction func login() {
        if usernameTextField.text == "lldo@lurado.com" && passwordTextField.text == "awesome" {
            showMessase("Access Granted 🎉")
        } else {
            showMessase("Access Denied 🚨")
        }
    }
}
