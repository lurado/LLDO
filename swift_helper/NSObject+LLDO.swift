//
//  NSObject+LLDO.swift
//  LLDO
//
//  Created by Sebastian Ludwig on 27.02.19.
//  Copyright © 2019 Julian Raschke und Sebastian Ludwig GbR. All rights reserved.
//

import Foundation

extension NSObject {
    /**
     Much nicer to type than `unsafeBitCast(, to:)`
     
     Returns the object at the given memory address casted to the type the method is called on.
     
     #### Example
     ```
     po UIView.at(0x7fd53e720630)
     ```
     */
    public static func at(_ address: Int) -> Self {
        return unsafeBitCast(address, to: self)
    }
}
