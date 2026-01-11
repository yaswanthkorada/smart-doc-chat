# Sidebar UX Testing Guide

## Quick Start

To test the sidebar improvements, follow these steps:

### 1. Restart the Streamlit App

```powershell
# Stop the current Streamlit instance (Ctrl+C)
# Then restart:
streamlit run app.py
```

Or use the start script:
```powershell
.\start.ps1
```

### 2. Test Cases

#### Test Case 1: Native Arrow Visibility
**Expected:** The native Streamlit collapse arrow (<<) should be visible at the top-left of the sidebar.

**Steps:**
1. Look at the top-left corner of the sidebar
2. You should see a white button with an arrow icon
3. Hover over it - it should turn light gray with a blue border

**✅ Pass Criteria:**
- Arrow is visible
- Button has white background
- Hover shows blue accent (#3B82F6)
- Smooth transition on hover

---

#### Test Case 2: Sidebar Collapse
**Expected:** Clicking the arrow should collapse the sidebar completely with no ghost strip.

**Steps:**
1. Click the collapse arrow (<<) button
2. Sidebar should smoothly slide away
3. Check the left edge of the screen

**✅ Pass Criteria:**
- Sidebar collapses smoothly (300ms animation)
- No empty strip or ghost sidebar remains
- Content area expands to use full width
- Arrow button remains visible at top-left corner

---

#### Test Case 3: Sidebar Expand
**Expected:** Clicking the arrow again should expand the sidebar.

**Steps:**
1. With sidebar collapsed, click the arrow button at top-left
2. Sidebar should smoothly slide in from the left

**✅ Pass Criteria:**
- Sidebar expands smoothly
- All sidebar content is visible
- Arrow button moves to sidebar header area
- No layout jumps or glitches

---

#### Test Case 4: Fallback Hamburger Toggle
**Expected:** A hamburger menu (☰) button provides an alternative toggle.

**Steps:**
1. Look for the hamburger (☰) button at top-left
2. Click it to toggle sidebar
3. Test multiple times

**✅ Pass Criteria:**
- Hamburger button is visible and clickable
- Toggles sidebar open/closed
- Has same styling as native arrow
- Works even if native arrow doesn't

---

#### Test Case 5: Hover States
**Expected:** All interactive elements show proper hover feedback.

**Steps:**
1. Hover over the toggle arrow button
2. Hover over the hamburger button (if visible)
3. Hover over sidebar buttons and dropdowns

**✅ Pass Criteria:**
- White background changes to light gray (#F8FAFC)
- Border changes to blue (#3B82F6)
- Smooth transition (120ms)
- No color flashing or jarring changes

---

#### Test Case 6: Keyboard Navigation
**Expected:** Toggle button is keyboard accessible.

**Steps:**
1. Press Tab until the toggle button is focused
2. Press Enter or Space to toggle sidebar
3. Check focus indicator visibility

**✅ Pass Criteria:**
- Button receives keyboard focus
- Blue focus ring is visible (3px, rgba(59, 130, 246, 0.3))
- Enter/Space keys toggle sidebar
- Focus remains manageable

---

#### Test Case 7: Content Area Adjustment
**Expected:** Main content area adjusts when sidebar toggles.

**Steps:**
1. With sidebar open, note content width
2. Collapse sidebar
3. Observe content area expansion
4. Expand sidebar again

**✅ Pass Criteria:**
- Content smoothly transitions to full width
- No overlapping with toggle button
- 60px left padding maintained for toggle button space
- No horizontal scrollbar appears

---

#### Test Case 8: Contrast and Readability
**Expected:** All text meets WCAG 2.1 AA contrast requirements.

**Steps:**
1. Check sidebar text against light gray background
2. Check toggle button text/icon against white background
3. Check hover states for contrast

**✅ Pass Criteria:**
- Dark text (#111827) on white (#FFFFFF): 16.6:1 ✅
- Dark text on light gray (#F8FAFC): 16.0:1 ✅
- Blue border (#3B82F6) visible on hover
- All text is readable without strain

---

#### Test Case 9: Responsive Behavior
**Expected:** Layout works on different screen sizes.

**Steps:**
1. Resize browser window to narrow width (<768px)
2. Test toggle functionality
3. Check for layout breaks

**✅ Pass Criteria:**
- Toggle button remains visible
- Sidebar behavior is consistent
- No horizontal overflow
- Touch targets are adequate (36x36px minimum)

---

#### Test Case 10: Theme Consistency
**Expected:** Sidebar matches the light theme throughout.

**Steps:**
1. Check sidebar background color
2. Check text colors
3. Check button and dropdown styling
4. Compare with main content area

**✅ Pass Criteria:**
- Sidebar has light gray background (#F8FAFC)
- All text is dark (#111827)
- Buttons have white backgrounds
- Dropdowns have white backgrounds with borders
- No gradient or dark purple backgrounds

---

## Common Issues and Fixes

### Issue 1: Native Arrow Not Visible
**Symptom:** The collapse arrow (<<) doesn't appear when sidebar is collapsed.

**Solution:**
1. Open DevTools (F12)
2. Inspect the area at top-left (16px, 16px)
3. Look for a button element
4. Check its `data-testid` attribute
5. Update CSS selector in `styles.css` line 360-370

**Example Fix:**
```css
/* If the testid changed */
[data-testid="NEW_TESTID_HERE"],
button[aria-label*="Open sidebar"] {
    position: fixed !important;
    /* ... rest of styling */
}
```

---

### Issue 2: Ghost Strip Still Visible
**Symptom:** An empty sidebar strip remains when collapsed.

**Solution:**
1. Open DevTools
2. Inspect the ghost strip element
3. Check its classes and data attributes
4. Add them to the collapsed state CSS in `styles.css` line 303-320

**Example Fix:**
```css
[data-testid="stSidebarCollapsed"],
.NEW_COLLAPSED_CLASS_HERE {
    width: 0 !important;
    visibility: hidden !important;
    /* ... rest of styling */
}
```

---

### Issue 3: Toggle Button Overlaps Content
**Symptom:** Toggle button covers text or interactive elements.

**Solution:**
Increase the left padding in `styles.css` line 324:
```css
.main .block-container {
    padding-left: 80px !important; /* Increased from 60px */
}
```

---

### Issue 4: Sidebar Text is White (Unreadable)
**Symptom:** Can't read sidebar text on light background.

**Solution:**
The legacy inline CSS in `app.py` might be overriding. Check lines 230-280 and ensure:
```css
[data-testid="stSidebar"] * {
    color: #111827 !important; /* Dark text, not white */
}
```

---

### Issue 5: Animations Are Janky
**Symptom:** Sidebar collapse/expand is not smooth.

**Solution:**
Check if hardware acceleration is enabled:
```css
[data-testid="stSidebar"] {
    will-change: transform, width;
    transform: translateZ(0); /* Force GPU acceleration */
}
```

---

## Browser-Specific Testing

### Chrome/Edge
- Use DevTools (F12) → Elements tab to inspect
- Check "Lighthouse" tab for accessibility audit
- Test keyboard navigation with Tab key

### Firefox
- Use Developer Tools (F12) → Inspector
- Check "Accessibility" panel for ARIA labels
- Test with NVDA screen reader (Windows)

### Safari (macOS)
- Use Web Inspector (Cmd+Option+I)
- Test with VoiceOver (Cmd+F5)
- Check retina display rendering

---

## Automated Testing (Future)

Consider adding these tests with Playwright or Selenium:

```python
# Example Playwright test
async def test_sidebar_toggle():
    await page.goto("http://localhost:8501")
    
    # Check sidebar is visible initially
    sidebar = await page.locator('[data-testid="stSidebar"]')
    assert await sidebar.is_visible()
    
    # Click collapse button
    toggle = await page.locator('button[data-testid="collapsedControl"]')
    await toggle.click()
    
    # Wait for animation
    await page.wait_for_timeout(400)
    
    # Check sidebar is hidden
    assert not await sidebar.is_visible()
    
    # Check no ghost strip
    ghost = await page.locator('.st-emotion-cache-stSidebarCollapsed')
    width = await ghost.evaluate('el => el.offsetWidth')
    assert width == 0
```

---

## Performance Checklist

- [ ] **Animation FPS:** 60fps during collapse/expand (check DevTools Performance)
- [ ] **CSS Load Time:** styles.css loads < 50ms
- [ ] **Reflow/Repaint:** Minimal layout shifts (use DevTools → Rendering)
- [ ] **Paint Flashing:** No excessive repaints (enable "Paint flashing")
- [ ] **Memory:** No memory leaks from toggling (check DevTools → Memory)

---

## Accessibility Audit

Run these tools for compliance verification:

1. **WAVE Browser Extension:** https://wave.webaim.org/extension/
2. **axe DevTools:** https://www.deque.com/axe/devtools/
3. **Lighthouse (Chrome):** DevTools → Lighthouse tab → Accessibility audit
4. **Manual Keyboard Test:** Navigate entire UI with Tab, Enter, Esc keys only

Expected Lighthouse Accessibility Score: **95+**

---

## Sign-Off Checklist

- [ ] All 10 test cases pass
- [ ] WCAG 2.1 AA contrast verified
- [ ] Keyboard navigation works
- [ ] No console errors or warnings
- [ ] Works on Chrome, Firefox, Edge, Safari
- [ ] Mobile/tablet responsive (if applicable)
- [ ] Documentation complete and accurate
- [ ] Code reviewed and committed

---

## Support

If you encounter issues not covered in this guide:

1. Check `SIDEBAR_UX_IMPROVEMENTS.md` for detailed implementation notes
2. Review Streamlit's DOM structure with DevTools
3. Consult Streamlit documentation: https://docs.streamlit.io
4. Contact developer: yaswanthkorada321@gmail.com

---

**Testing Date:** _______________  
**Tested By:** _______________  
**Browser Version:** _______________  
**Result:** ⬜ PASS  ⬜ FAIL (Notes: ________________)
