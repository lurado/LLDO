//
//  UIView+LLDO.swift
//      
//
//  Created by Sebastian Ludwig on 24.02.19.
//  Copyright (c) 2019 Julian Raschke und Sebastian Ludwig GbR. All rights reserved.
//

import UIKit

extension UIView {
    // MARK: - Navigation -
    
    /**
     View of the root view controller.
     
     #### Example
     
     ```
     po UIView.root
     ```
     */
    @objc static var root: UIView {
        return UIApplication.shared.keyWindow!.rootViewController!.view
    }
    
    /**
     View of the current view controller.
     
     - SeeAlso: `UIViewController.current`
     
     #### Example
     
     ```
     po UIView.current
     ```
     */
    @objc static var current: UIView {
        return UIViewController.current.view
    }
    
    /**
     Returns the view and all its subviews in sequence.
     
     This method provides an easy way to iterate over a (sub-)tree of the view hierarchy.
     The views are ordered by nesting level: first the view, then all subviews, then all sub-subviews and so on.
     
     - Parameter depth: Maximum level of views to visit. For example, pass `1` to only visit the view itself or `2` for the view and its immediate subviews.
     - Returns: The view and all its subviews in level order.
     
     #### Example
     
     ```
     po UIView.current.tree()
     po UIView.current.tree().filter { $0.isHidden } // only hidden views
     po Array(UIView.current.tree(depth: 2))[2]      // the second subiew
     ```
     */
    func tree(depth: Int = .max) -> UnfoldSequence<UIView, [(UIView, Int)]> {
        return sequence(state: [(self, 1)]) { state in
            guard !state.isEmpty else { return nil }
            let (view, level) = state.removeFirst()
            if level < depth {
                state.append(contentsOf: view.subviews.map({ ($0, level + 1) }))
            }
            return view
        }
    }
}

extension UIView {
    // MARK: - Search by Type -
    
    /**
     Returns subviews of the given type.
     
     #### Example
     
     ```
     po UIView.current.all(UILabel.self)
     ```
     */
    func all<T: UIView>(_: T.Type) -> [T]  {
        return tree()
            .compactMap { $0 as? T }
    }
    
    /**
     Returns the first subview of a given type.
     
     Optionally a condition predicate can be passed.
     If, like in the third example, the predicate parameter is typed, the method parameter may be omitted.
     However either of them _must_ be defined.
     
     - Parameter type: Subview type constraint (optional).
     - Parameter predicate: Condition hat must be fulfilled by a subview (optional).
     
     - Returns: Returns the first subview of the given type that matches the predicate.
     
     #### Example
     
     ```
     po UIView.current.first(UILabel.self)
     po UIView.current.first(UILabel.self) { $0.text == "Lorem" }
     po UIView.current.first { (l: UILabel) in l.text == "Lorem" }
     ```
     */
    func first<T: UIView>(_ type: T.Type, where predicate: ((T) -> Bool)? = nil) -> T?  {
        let predicate = predicate ?? { _ in true }
        return all(T.self).first(where: predicate)
    }
    
    /// :nodoc:
    /// this method handles the third example case of the previous method
    func first<T: UIView>(where predicate: ((T) -> Bool)? = nil) -> T?  {
        return first(T.self, where: predicate)
    }
    
    /**
     Returns the first subview of the calling type in the given view.
     
     This method is an alternatively flavored `UIView.first(_:where:)` to not have to type the `.self`.
     
     #### Example
     
     ```
     po UILabel.first(in: UIView.current)
     ```
     */
    @objc static func first(in root: UIView = UIView.current) -> Self? {
        return root.first(self) { _ in true }
    }
}

extension UIView {
    // MARK: - Search by Content -
    
    /**
     A Boolean indicating whether the view contains a given text.
     
     The following properties will be checked:
     
     - `UILabel.text`
     - `UITextField.text` and `.placeholer`
     - `UITextView.text`
     - `UIButton.currentTitle`
     
     If any of these attributes contains the passed text, the method will return `true`.
     All other cases will return `false`.
     
     - Parameter pattern: Regex pattern that must be matched.
     
     #### Example
     
     ```
     po UILabel.first()?.containsText("name")
     ```
     */
    @objc func containsText(_ pattern: String) -> Bool {
        let check = { (text: String?) in
            return text == nil ? false : try! NSRegularExpression(pattern: pattern).firstMatch(in: text!, options: [], range: NSRange(location: 0, length: text!.utf16.count)) != nil
        }
        if let label = self as? UILabel {
            return check(label.text)
        } else if let textField = self as? UITextField {
            return check(textField.text) || check(textField.placeholder)
        } else if let textView = self as? UITextView {
            return check(textView.text)
        } else if let button = self as? UIButton {
            return check(button.currentTitle)
        } else {
            return false
        }
    }
    
    /**
     Returns all views that contain the given text.
     
     Traverses the view hierarchy starting at the receiver and returns all views whose `containsText(_:)` check returns `true`.
     
     - Parameter pattern: Regex pattern that must be matched.
     - Remark: The labels of `UIButtons` will be excluded.
     - SeeAlso: `containsText(_:)`
     
     #### Example
     
     ```
     po UIView.current.grep("o")
     ```
     */
    @objc func grep(_ pattern: String) -> [UIView] {
        return tree()
            .compactMap { view in
                let matches = view.containsText(pattern) && type(of: view).description() != "UIButtonLabel"
                return matches ? view : nil
        }
    }
    
    /**
     Returns all views that contain the given text.
     
     This method is an alternative to `grep(_:)` to allow for a different calling style.
     
     - SeeAlso: `grep(_:)`
     
     #### Example
     
     ```
     po UIView.grep("o")
     po UIView.grep("o", in: UIView.current)
     ```
     */
    @objc static func grep(_ pattern: String, in root: UIView = UIView.root) -> [UIView] {
        return root.grep(pattern)
    }
    
    /**
     Returns the first view with the given accessibility identifier.
     
     Traverses the view hierarchy starting at the reciever and returns the first view whose `accessibilityIdentifier` equals or contains the passed in identifier.
     
     - SeeAlso: `first(in:)`
     
     #### Example
     
     ```
     po UIView.current.find(byAccessibilityID: "username_input")
     ```
     */
    @objc func find(byAccessibilityID accessibilityIdentifier: String) -> UIView? {
        return first { (view: UIView) in view.accessibilityIdentifier?.range(of: accessibilityIdentifier) != nil }
    }
    
    /**
     Returns the first view with the given accessibility identifier.
     
     This method is an alternative to `find(byAccessibilityID:)` to allow for a different calling style.
     
     - SeeAlso: `find(byAccessibilityID:)`
     
     #### Example
     
     ```
     po UIView.find(byAccessibilityID: "username_input")
     po UIView.find(byAccessibilityID: "username_input", in: UIView.current)
     ```
     */
    static func find(byAccessibilityID accessibilityIdentifier: String, in root: UIView = UIView.root) -> UIView? {
        return root.find(byAccessibilityID: accessibilityIdentifier)
    }
}

extension UIView {
    // MARK: - Interaction -
    
    /**
     Sets the text of the closest `UITextField` or `UITextView`.
     
     The `.text` property of the first `UITextField` or `UITextView` found in the view hieararchy, starting at the receiver, is set to the passed text.
     
     - SeeAlso: `first(in:)`
     
     #### Example
     
     ```
     po UITextField.first()?.enterText("lldo@lurado.com")
     ```
     */
    @objc func enterText(_ text: String) {
        if let textField = UITextField.first(in: self) {
            textField.text = text
        } else if let textView = UITextView.first(in: self) {
            textView.text = text
        }
        caflush()
    }
    
    /**
     Taps the closest button.
     
     A `.touchUpInside` event is sent to the first `UIButton` found in the view hiearchy, starting at the receiver.
     
     - SeeAlso: `first(in:)`
     
     #### Example
     
     ```
     po UIButton.first()?.tap()
     ```
     */
    @objc func tap() {
        UIButton.first(in: self)?.sendActions(for: .touchUpInside)
        caflush()
    }
    
    /**
     Slides the closest `UISwitch` or `UISlider`.
     
     Looks for the first `UISwitch` or `UISlider` in the view hierarchy, starting at the receiver.
     If a `UISwitch` is found, a value of `0` deactivates the it, every value other than `0` activates it.
     Don't pass any value to toggle the switch.
     
     A `UISlider` will be set to the vaue you pass.
     
     - SeeAlso: `first(in:)`
     
     #### Example
     
     ```
     po UISwitch.first()?.slide(1)
     po UISwitch.first()?.slide()
     ```
     */
    func slide(toValue value: Float? = nil) {
        if let uiswitch = UISwitch.first(in: self) {
            if let value = value {
                uiswitch.setOn(value != 0, animated: false)
            } else {
                uiswitch.setOn(!uiswitch.isOn, animated: false)
            }
        } else if let slider = UISlider.first(in: self), let value = value {
            slider.setValue(value, animated: false)
        }
        caflush()
    }
}

extension UIView {
    // MARK: - Highlighting -
    
    /**
     Colors the areas covered by given insets.
     
     - Parameters:
         - hightlight: Pass `true` to add the highlight, pass `false` to remove it.
         - insets: The insets to highlight.
         - color: The highlight color.
         - identifier: Unique identifier for the highlight. Used to distinguish between multiple highlights that are active at the same time.
     
     #### Example
     
     ```
     po UIView.current.highlight(true, insets: UIEdgeInsets(top: 8, left: 8, bottom: 8, right: 8))
     po UIView.current.highlight(false)
     ```
     */
    @objc func highlight(_ highlight: Bool, insets: UIEdgeInsets = .zero, color: UIColor = UIColor.red.withAlphaComponent(0.3), identifier: String = "inset_highlight") {
        defer { caflush() }
        
        layer.sublayers?.filter { $0.name == identifier }.forEach { $0.removeFromSuperlayer() }
        
        if !highlight {
            return
        }
        
        func createLayer(x: CGFloat, y: CGFloat, width: CGFloat, height: CGFloat) -> CALayer {
            let layer = CALayer()
            layer.frame = CGRect(x: x, y: y, width: width, height: height)
            layer.backgroundColor = color.cgColor
            layer.name = identifier
            return layer
        }
        
        let layers = [
            createLayer(x: 0, y: 0, width: insets.left, height: bounds.height),
            createLayer(x: bounds.width - insets.right, y: 0, width: insets.right, height: bounds.height),
            createLayer(x: insets.left, y: 0, width: bounds.width - insets.left - insets.right, height: insets.top),
            createLayer(x: insets.left, y: bounds.height - insets.bottom, width: bounds.width - insets.left - insets.right, height: insets.top)
        ]
        layers.forEach { layer.addSublayer($0) }
    }
    
    /**
     Highlights the safe area insets of the receiver.
     
     Basically this is a runtime variant of Interface Builder's _Editor > Canvas > Show Layout Rectangles_.
     
     - Parameters:
        - hightlight: Pass `true` to add the highlight, pass `false` to remove it.
        - color: The highlight color.
        - depth: Level of subviews to process. Pass `1` to only highlight the insets on the view itself, pass `2` to also highlight the insets of its subviews and so on.
     
     #### Example
     
     ```
     po UIView.current.highlightSafeAreaInsets()
     po UIView.current.highlightSafeAreaInsets(false)
     po UIView.current.highlightSafeAreaInsets(depth: 5)
     po UIView.current.highlightSafeAreaInsets(false, depth: .max)
     ```
     */
    @objc func highlightSafeAreaInsets(_ highlight: Bool = true, color: UIColor = UIColor.blue.withAlphaComponent(0.3), depth: Int = 1) {
        tree(depth: depth).forEach { view in
            view.highlight(highlight, insets: view.safeAreaInsets, color: color, identifier: "safe_area_highlight")
        }
    }
    
    /**
     Highlights the layout margins of the receiver.
     
     Basically this is a runtime variant of Interface Builder's _Editor > Canvas > Show Layout Rectangles_.
     
     - Parameters:
        - hightlight: Pass `true` to add the highlight, pass `false` to remove it.
        - color: The highlight color.
        - depth: Level of subviews to process. Pass `1` to only highlight the layout margins on the view itself, pass `2` to also highlight the layout margins of its subviews and so on.
     
     #### Example
     
     ```
     po UIView.current.highlightLayoutMargins()
     po UIView.current.highlightLayoutMargins(false)
     po UIView.current.highlightLayoutMargins(depth: 2)
     po UIView.current.highlightLayoutMargins(false, depth: .max)
     ```
     */
    @objc func highlightLayoutMargins(_ highlight: Bool = true, color: UIColor = UIColor.green.withAlphaComponent(0.3), depth: Int = 1) {
        tree(depth: depth).forEach { view in
            view.highlight(highlight, insets: view.layoutMargins, color: color, identifier: "layout_margins_highlight")
        }
    }
}

extension UIView {
    // MARK: - Display -
    
    /**
     Displays visual view changes that have been made while the program execution was paused.
     
     Normally visual changes to a view from LLDB, like changing the background color, don't show up until the program execution is continued.
     Such an update can be forced while the program remains paused by calling this method. Internally this method calls `CATransaction.flush()`.
     
     - SeeAlso: `CATransaction.flush()`
     
     #### Example
     
     ```
     expr UIView.current.backgroundColor = .orange
     // still not red
     expr UIView.current.caflush()
     // now it's red
     ```
     */
    @objc func caflush() {
        CATransaction.flush()
    }
    
    /**
     Saves a snapshot of the view as image.
     
     The receiving view is rendered as PNG and saved to disk.
     If no destination path is specified, the image will be saved in the apps temporary directory.
     On the simulator the image can then directly be opened.
     As a convenience the necessary `shell open` command is printed to the console.
     
     - Parameter path: Destination path where to save the view screenshot to.
     
     #### Example
     
     ```
     po UIView.current.screenshot("/some/absolute/path.png")
     shell open /some/absolute/path.png
     ```
     */
    @objc func screenshot(_ path: String? = nil) {
        let fileURL = path != nil ? URL(fileURLWithPath: path!) : FileManager.default.temporaryDirectory.appendingPathComponent("\(UUID.init().uuidString).png")
        let renderer = UIGraphicsImageRenderer(bounds: bounds)
        let png = renderer.pngData { _ in
            self.drawHierarchy(in: bounds, afterScreenUpdates: false)
        }
        do {
            try png.write(to: fileURL)
            print("shell open \(fileURL.absoluteString)")
        } catch let e {
            print("Failed to write \(fileURL): \(e)")
        }
    }
    
    /**
     Displays a semi transparent image on top of the receiver to be able to visually compare it to a reference design.
     
     An `UIImageView` displaying the image will be created and added as a subview.
     It will be semi transparent so any differences are easy to spot.
     The content mode is set to `.scaleAspectFit` to avoid deformations.
     
     - Parameter image: Image to overlay. Pass `nil` to remove the overlay.
     - Returns: The created `UIImageView`
     - Remark: This method unfolds its real utility within the `proofimage` LLDB command.
     
     #### Example
     
     ```
     po UIView.current.overlay(UIImage(named: "reference.png"))
     ```
     */
    @objc func overlay(_ image: UIImage? = nil) -> UIImageView? {
        defer { caflush() }
        
        let layerName = "proofimage"
        
        layer.sublayers?.filter { $0.name == layerName }.forEach { $0.removeFromSuperlayer() }
        
        guard let image = image else { return nil }
        
        let imageView = UIImageView(image: image)
        imageView.layer.name = layerName
        imageView.alpha = 0.3
        imageView.frame = bounds
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        addSubview(imageView)
        return imageView
    }
}
