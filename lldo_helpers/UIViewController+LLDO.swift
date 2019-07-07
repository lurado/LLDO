//
//  UIViewController+LLDO.swift
//  LLDO
//
//  Created by Sebastian Ludwig on 24.02.19.
//  Copyright (c) 2019 Julian Raschke und Sebastian Ludwig GbR. All rights reserved.
//

import UIKit

extension UIViewController {
    /**
     The current as in top most view controller.
     
     When determining the current view controller the following rules are applied recursively:
     
     - Start with the window's root view controller
     - If a view controller is presented, select it
     - For a navigation controller, select the top view controller
     - For a tab bar controller, select the selected view controller
     - For a custom container view controller, select the last child view controller
     
     #### Example
     
         po UIViewController.current
     */
    @objc static var current: UIViewController {
        func topMostViewController(startingAt viewController: UIViewController) -> UIViewController {
            if let modalViewController = viewController.presentedViewController  {
                return topMostViewController(startingAt: modalViewController)
            } else if let topViewController = (viewController as? UINavigationController)?.topViewController {
                return topMostViewController(startingAt: topViewController)
            } else if let selectedViewController = (viewController as? UITabBarController)?.selectedViewController {
                return topMostViewController(startingAt: selectedViewController)
            } else if let lastChildViewController = viewController.children.last {
                return topMostViewController(startingAt: lastChildViewController)
            } else {
                return viewController
            }
        }
        return topMostViewController(startingAt: UIApplication.shared.keyWindow!.rootViewController!)
    }
}
